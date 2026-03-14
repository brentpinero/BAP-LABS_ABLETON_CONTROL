#!/usr/bin/env python3
"""
LLM LoRA Fine-Tuning Pipeline for Audio-Aware Music Production Assistant
=========================================================================
Trains Qwen3-4B with LoRA to understand audio embeddings from our CNN encoder.

Architecture (from jonflynng/qwen2-audio-finetune analysis):
1. CNN Audio Encoder produces 512-dim embeddings
2. MLP Projector maps to LLM hidden dim (2048 for Qwen3-4B)
3. Audio embeddings injected as special tokens in conversation
4. LoRA fine-tuning on all projection layers

Training Strategy:
- Stage 1: Alignment pre-training (audio → text description)
- Stage 2: Instruction fine-tuning (multi-turn conversations)

Usage:
    # Quick test run
    python train_llm_lora.py --test

    # Full training
    python train_llm_lora.py --epochs 3 --batch-size 1

    # Resume from checkpoint
    python train_llm_lora.py --resume checkpoints/llm_lora/best_model
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Hugging Face imports
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
    BitsAndBytesConfig,
)
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    PeftModel,
    prepare_model_for_kbit_training,
)
from tqdm import tqdm

# Local imports (optional — these modules are not yet implemented)
try:
    from cnn_audio_encoder import SerumAudioEncoder
    from audio_llm_projector import AudioLLMBridge, AudioToLLMProjector
    from serum_params import CNN_PARAMS, LLM_PARAMS, PARAM_DESCRIPTIONS
except ImportError:
    SerumAudioEncoder = None
    AudioLLMBridge = None
    AudioToLLMProjector = None
    CNN_PARAMS = LLM_PARAMS = PARAM_DESCRIPTIONS = None


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class TrainingConfig:
    """Training configuration with defaults from jonflynng analysis."""

    # Model
    base_model: str = "Qwen/Qwen2.5-3B-Instruct"  # Start with 3B, upgrade to 4B when available
    cnn_checkpoint: str = "checkpoints/best_model.pt"

    # LoRA configuration (from jonflynng: r=128, alpha=256)
    # We use slightly smaller for 3B model
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj",      # MLP
    ])

    # Training hyperparameters (from jonflynng)
    num_epochs: int = 3
    batch_size: int = 1  # Small due to memory constraints
    gradient_accumulation_steps: int = 8
    learning_rate: float = 1e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    max_grad_norm: float = 10.0

    # Optimization
    optim: str = "adamw_torch"  # Use adamw_8bit for memory savings if needed
    lr_scheduler_type: str = "cosine"
    gradient_checkpointing: bool = True

    # Quantization (for M4 Max memory efficiency)
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_quant_type: str = "nf4"

    # Audio embedding
    cnn_dim: int = 512
    llm_hidden_dim: int = 2048  # Qwen3-4B hidden size
    max_audio_tokens: int = 8   # Max audio embeddings per turn

    # Sequence lengths
    max_seq_length: int = 2048

    # Paths
    output_dir: str = "checkpoints/llm_lora"
    data_dir: str = "data/llm_training"

    # Logging
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100


# =============================================================================
# SPECIAL TOKENS FOR AUDIO
# =============================================================================

AUDIO_TOKENS = {
    "audio_start": "<|audio_start|>",
    "audio_end": "<|audio_end|>",
    "audio_embed": "<|audio|>",  # Placeholder replaced with actual embeddings
    "track_bass": "<|track:bass|>",
    "track_lead": "<|track:lead|>",
    "track_pad": "<|track:pad|>",
    "track_drums": "<|track:drums|>",
    "track_fx": "<|track:fx|>",
    "track_master": "<|track:master|>",
}


# =============================================================================
# CONVERSATION FORMAT
# =============================================================================

def format_audio_conversation(
    user_text: str,
    assistant_response: str,
    audio_descriptions: Optional[List[Dict]] = None,
    system_prompt: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    Format a conversation turn with optional audio context.

    Audio descriptions format:
    [
        {"track": "bass", "description": "Low sub bass with slow attack"},
        {"track": "lead", "description": "Bright saw lead with high resonance"},
    ]
    """
    messages = []

    # System prompt for music production context
    if system_prompt is None:
        system_prompt = """You are an expert music production assistant specializing in sound design and synthesis.
You can analyze audio characteristics and suggest parameter adjustments for Serum synthesizer.
When audio is provided, analyze its tonal qualities, envelope characteristics, and spectral content.
Provide specific, actionable advice for achieving desired sounds."""

    messages.append({"role": "system", "content": system_prompt})

    # Build user message with audio context
    user_content = ""

    if audio_descriptions:
        user_content += f"{AUDIO_TOKENS['audio_start']}\n"
        for audio in audio_descriptions:
            track = audio.get("track", "other")
            desc = audio.get("description", "")
            track_token = AUDIO_TOKENS.get(f"track_{track}", "<|track:other|>")
            user_content += f"{track_token} {desc}\n"
        user_content += f"{AUDIO_TOKENS['audio_end']}\n\n"

    user_content += user_text
    messages.append({"role": "user", "content": user_content})

    # Assistant response
    messages.append({"role": "assistant", "content": assistant_response})

    return messages


# =============================================================================
# DATASET
# =============================================================================

class AudioLLMDataset(Dataset):
    """
    Dataset for audio-aware LLM training.

    Each sample contains:
    - input_ids: Tokenized conversation
    - attention_mask: Attention mask
    - labels: Labels for causal LM (masked for user turns)
    - audio_embeddings: Optional CNN embeddings for audio context
    """

    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 2048,
        include_audio: bool = False,
        cnn_encoder: Optional[nn.Module] = None,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.include_audio = include_audio
        self.cnn_encoder = cnn_encoder

        # Load training data
        self.samples = self._load_data(data_path)
        print(f"Loaded {len(self.samples)} training samples")

    def _load_data(self, data_path: str) -> List[Dict]:
        """Load training data from JSON or JSONL."""
        path = Path(data_path)

        if not path.exists():
            print(f"Warning: Data path {data_path} not found. Using empty dataset.")
            return []

        if path.suffix == ".jsonl":
            samples = []
            with open(path, 'r') as f:
                for line in f:
                    samples.append(json.loads(line))
            return samples
        else:
            with open(path, 'r') as f:
                return json.load(f)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]

        # Get conversation messages
        messages = sample.get("messages", [])
        if not messages:
            # Convert from simple format
            messages = format_audio_conversation(
                user_text=sample.get("user", ""),
                assistant_response=sample.get("assistant", ""),
                audio_descriptions=sample.get("audio", None),
            )

        # Apply chat template
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"].squeeze(0)
        attention_mask = encoding["attention_mask"].squeeze(0)

        # Create labels (same as input_ids for causal LM)
        # In a more sophisticated setup, we'd mask user turns
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100  # Mask padding

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


# =============================================================================
# MODEL SETUP
# =============================================================================

def setup_model_and_tokenizer(config: TrainingConfig) -> Tuple[Any, Any]:
    """
    Setup Qwen model with LoRA and quantization.

    Returns:
        model: PeftModel with LoRA adapters
        tokenizer: Tokenizer with special audio tokens
    """
    print(f"\n{'='*60}")
    print(f"Setting up model: {config.base_model}")
    print(f"{'='*60}")

    # Quantization config for memory efficiency
    bnb_config = None
    if config.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=getattr(torch, config.bnb_4bit_compute_dtype),
            bnb_4bit_quant_type=config.bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=True,
        )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.base_model,
        trust_remote_code=True,
        padding_side="right",
    )

    # Add special audio tokens
    special_tokens = list(AUDIO_TOKENS.values())
    tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Tokenizer vocab size: {len(tokenizer)}")
    print(f"Added {len(special_tokens)} special audio tokens")

    # Load model
    print(f"\nLoading base model...")
    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if not config.use_4bit else None,
    )

    # Resize embeddings for new tokens
    model.resize_token_embeddings(len(tokenizer))

    # Prepare for k-bit training if using quantization
    if config.use_4bit:
        model = prepare_model_for_kbit_training(model)

    # LoRA configuration (from jonflynng analysis)
    print(f"\nApplying LoRA...")
    print(f"  r={config.lora_r}, alpha={config.lora_alpha}")
    print(f"  Target modules: {config.lora_target_modules}")

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.lora_target_modules,
        bias="none",
    )

    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nTrainable parameters: {trainable_params:,} ({100*trainable_params/total_params:.2f}%)")
    print(f"Total parameters: {total_params:,}")

    return model, tokenizer


# =============================================================================
# TRAINING
# =============================================================================

def train(config: TrainingConfig, resume_from: Optional[str] = None):
    """Main training function."""

    print("\n" + "="*60)
    print("AUDIO-AWARE LLM FINE-TUNING")
    print("="*60)

    # Create output directory
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save config
    config_path = output_dir / "training_config.json"
    with open(config_path, 'w') as f:
        # Convert dataclass to dict, handling list fields
        config_dict = {k: v for k, v in config.__dict__.items()}
        json.dump(config_dict, f, indent=2)

    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(config)

    # Create dataset
    print(f"\nLoading training data...")
    data_path = Path(config.data_dir) / "train.jsonl"

    if not data_path.exists():
        print(f"Creating placeholder training data at {data_path}")
        create_placeholder_data(data_path)

    train_dataset = AudioLLMDataset(
        data_path=str(data_path),
        tokenizer=tokenizer,
        max_length=config.max_seq_length,
    )

    # Validation dataset (optional)
    val_dataset = None
    val_path = Path(config.data_dir) / "val.jsonl"
    if val_path.exists():
        val_dataset = AudioLLMDataset(
            data_path=str(val_path),
            tokenizer=tokenizer,
            max_length=config.max_seq_length,
        )
        print(f"Validation samples: {len(val_dataset)}")

    # Data collator
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        return_tensors="pt",
    )

    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        weight_decay=config.weight_decay,
        warmup_ratio=config.warmup_ratio,
        max_grad_norm=config.max_grad_norm,
        optim=config.optim,
        lr_scheduler_type=config.lr_scheduler_type,
        gradient_checkpointing=config.gradient_checkpointing,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        eval_steps=config.eval_steps if val_dataset else None,
        evaluation_strategy="steps" if val_dataset else "no",
        save_total_limit=3,
        load_best_model_at_end=val_dataset is not None,
        report_to="none",  # Disable wandb/tensorboard for now
        bf16=True,
        dataloader_num_workers=0,  # Avoid multiprocessing issues on macOS
    )

    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # Resume from checkpoint if specified
    resume_checkpoint = None
    if resume_from:
        resume_checkpoint = resume_from
        print(f"\nResuming from: {resume_checkpoint}")

    # Train!
    print(f"\n{'='*60}")
    print("Starting training...")
    print(f"{'='*60}\n")

    start_time = time.time()
    trainer.train(resume_from_checkpoint=resume_checkpoint)
    total_time = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"Training complete!")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"{'='*60}")

    # Save final model
    final_path = output_dir / "final_model"
    model.save_pretrained(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    print(f"Saved final model to: {final_path}")

    return model, tokenizer


# =============================================================================
# PLACEHOLDER DATA GENERATION
# =============================================================================

def create_placeholder_data(output_path: Path):
    """
    Create minimal placeholder training data.

    This will be replaced by the synthetic QA generator.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Sample conversations about synth parameters
    samples = [
        {
            "user": "How do I make a bass sound more subby?",
            "assistant": "To make your bass sound more subby, focus on these Serum parameters:\n\n1. **Lower the filter cutoff** (fil_cutoff_hz) - Start around 200-400Hz to remove high frequencies\n2. **Reduce oscillator octave** (a_octave) - Try -1 or -2 octaves for deeper fundamentals\n3. **Minimize unison detune** (a_unidet) - Keep it low to maintain a focused, centered low end\n4. **Use a sine or triangle wavetable** - Position a_wtpos at the start of Basic Shapes\n\nThe key is removing harmonic content while keeping the fundamental strong.",
            "audio": None,
        },
        {
            "user": "The attack on my lead is too slow, how do I fix it?",
            "assistant": "To get a faster attack on your lead sound, adjust these parameters:\n\n1. **Reduce env1_atk_ms** (amp envelope attack) - Set it to 0-5ms for instant transients\n2. **Check env2_atk_ms** (filter envelope attack) - If your filter is modulated, make this fast too\n3. **Lower a_warp** if using warp modes that add attack time\n\nFor plucky, percussive leads, you want near-zero attack times. The sound should hit immediately when you press a key.",
            "audio": None,
        },
        {
            "user": "I want more width in my pad sound",
            "assistant": "For wider pad sounds in Serum, try these techniques:\n\n1. **Increase unison voices** (a_unison) - Use 4-8 voices for rich stereo spread\n2. **Boost unison detune** (a_unidet) - Higher values = wider stereo image\n3. **Add chorus** (cho_wet) - Even subtle chorus adds dimension\n4. **Pan oscillators** - Set a_pan and b_pan to opposite sides\n5. **Use stereo wavetables** or warp modes that create stereo movement\n\nThe combination of detuned unison voices with subtle chorus creates lush, wide pads that fill the stereo field.",
            "audio": None,
        },
    ]

    with open(output_path, 'w') as f:
        for sample in samples:
            f.write(json.dumps(sample) + '\n')

    print(f"Created placeholder data with {len(samples)} samples at {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Train Audio-Aware LLM with LoRA")

    # Training args
    parser.add_argument('--epochs', type=int, default=3,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=1,
                        help='Per-device batch size')
    parser.add_argument('--lr', type=float, default=1e-5,
                        help='Learning rate')

    # LoRA args
    parser.add_argument('--lora-r', type=int, default=64,
                        help='LoRA rank')
    parser.add_argument('--lora-alpha', type=int, default=128,
                        help='LoRA alpha')

    # Model args
    parser.add_argument('--model', type=str, default="Qwen/Qwen2.5-3B-Instruct",
                        help='Base model name or path')
    parser.add_argument('--no-4bit', action='store_true',
                        help='Disable 4-bit quantization')

    # Data args
    parser.add_argument('--data-dir', type=str, default='data/llm_training',
                        help='Training data directory')

    # Checkpoint args
    parser.add_argument('--resume', type=str, default=None,
                        help='Resume from checkpoint')
    parser.add_argument('--output-dir', type=str, default='checkpoints/llm_lora',
                        help='Output directory')

    # Test mode
    parser.add_argument('--test', action='store_true',
                        help='Quick test run (1 epoch, minimal data)')

    args = parser.parse_args()

    # Build config
    config = TrainingConfig()
    config.num_epochs = args.epochs
    config.batch_size = args.batch_size
    config.learning_rate = args.lr
    config.lora_r = args.lora_r
    config.lora_alpha = args.lora_alpha
    config.base_model = args.model
    config.use_4bit = not args.no_4bit
    config.data_dir = args.data_dir
    config.output_dir = args.output_dir

    # Test mode overrides
    if args.test:
        config.num_epochs = 1
        config.logging_steps = 1
        config.save_steps = 50
        print("TEST MODE: 1 epoch, frequent logging")

    # Run training
    train(config, resume_from=args.resume)


if __name__ == '__main__':
    main()

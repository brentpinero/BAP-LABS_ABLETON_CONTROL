#!/bin/bash

# Monitor Final GPT-5 Pipeline Progress

echo "🎛️  GPT-5 FINAL SERUM PIPELINE MONITOR"
echo "====================================="
echo ""

# Check if pipeline is running
if ps aux | grep -q "[p]ython gpt5_serum_mistral_pipeline.py"; then
    echo "✅ Pipeline Status: RUNNING"
else
    echo "❌ Pipeline Status: STOPPED"
    exit 1
fi

echo ""
echo "📊 PROGRESS METRICS:"
echo "-------------------"

# Count completed batches
BATCHES=$(grep "Completed batch" final_pipeline.log | tail -1)
echo "  $BATCHES"

# Count total accepted examples
ACCEPTED=$(grep -c "✅ Accepted" final_pipeline.log)
echo "  Total accepted examples: $ACCEPTED"

# Count processed presets
PROCESSED=$(grep -c "Processing preset:" final_pipeline.log)
echo "  Presets processed: $PROCESSED"

# Count filtered examples
FILTERED=$(grep -c "❌ Filtered" final_pipeline.log)
echo "  Filtered examples: $FILTERED"

# Calculate acceptance rate
if [ $ACCEPTED -gt 0 ]; then
    TOTAL_GENERATED=$((ACCEPTED + FILTERED))
    ACCEPTANCE_RATE=$(awk "BEGIN {printf \"%.1f\", ($ACCEPTED/$TOTAL_GENERATED)*100}")
    echo "  Acceptance rate: ${ACCEPTANCE_RATE}%"
fi

echo ""
echo "🎯 RECENT ACTIVITY (last 5 examples):"
echo "------------------------------------"
grep "✅ Accepted" final_pipeline.log | tail -5 | sed 's/.*overall=0.97 (/  • /' | sed 's/)$//'

echo ""
echo "⏱️  TIMING:"
echo "----------"
START_TIME=$(head -1 final_pipeline.log | awk '{print $1, $2}')
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "  Started: $START_TIME"
echo "  Current: $CURRENT_TIME"

echo ""
echo "💾 LOG SIZE:"
echo "-----------"
ls -lh final_pipeline.log | awk '{print "  " $5}'

echo ""
echo "====================================="
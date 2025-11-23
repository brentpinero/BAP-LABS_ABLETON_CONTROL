#!/usr/bin/env node
/**
 * Max for Live <-> Flask API Bridge (Node.js version)
 * Accepts commands via Max's node.script, sends HTTP requests, returns JSON
 * This allows Max to communicate with the Flask API server
 */

const http = require('http');
const Max = require('max-api');

const API_HOST = 'localhost';
const API_PORT = 8080;

/**
 * Make HTTP request to Flask server
 */
function makeRequest(method, path, data = null) {
    return new Promise((resolve, reject) => {
        // Prepare request body if data is provided
        const requestBody = data ? JSON.stringify(data) : null;

        const options = {
            hostname: API_HOST,
            port: API_PORT,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        // Add Content-Length header for POST/PUT requests
        if (requestBody) {
            options.headers['Content-Length'] = Buffer.byteLength(requestBody);
        }

        const req = http.request(options, (res) => {
            let body = '';

            res.on('data', (chunk) => {
                body += chunk;
            });

            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(body);
                    resolve({ status: res.statusCode, data: jsonData });
                } catch (e) {
                    resolve({ status: res.statusCode, data: body });
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        // Send data if provided
        if (requestBody) {
            req.write(requestBody);
        }

        req.end();
    });
}

/**
 * Check if API server is running
 */
async function checkHealth() {
    try {
        const result = await makeRequest('GET', '/health');

        if (result.status === 200) {
            return {
                status: 'success',
                server: 'healthy',
                model_loaded: result.data.model_loaded || false
            };
        } else {
            return {
                status: 'error',
                message: `Server returned ${result.status}`
            };
        }
    } catch (error) {
        return {
            status: 'error',
            message: error.message
        };
    }
}

/**
 * Generate preset from text description
 */
async function generatePreset(description) {
    try {
        const result = await makeRequest('POST', '/generate', { description });

        if (result.status === 200) {
            return {
                status: 'success',
                preset: result.data
            };
        } else {
            return {
                status: 'error',
                message: `Server returned ${result.status}`
            };
        }
    } catch (error) {
        return {
            status: 'error',
            message: error.message
        };
    }
}

/**
 * Handle incoming messages from Max
 */
Max.addHandler('health', async () => {
    const result = await checkHealth();
    Max.outlet(JSON.stringify(result));
});

Max.addHandler('generate', async (requestJson) => {
    try {
        // Parse the JSON request from Max
        Max.post(`[Bridge] Received generate request: ${requestJson}`);
        const request = JSON.parse(requestJson);
        const description = request.description || '';
        Max.post(`[Bridge] Description: ${description}`);

        const result = await generatePreset(description);
        Max.post(`[Bridge] Result status: ${result.status}`);
        Max.outlet(JSON.stringify(result));
    } catch (error) {
        Max.post(`[Bridge] Error: ${error.message}`);
        Max.outlet(JSON.stringify({
            status: 'error',
            message: `Failed to parse request: ${error.message}`
        }));
    }
});

// Startup message
Max.post('M1 API Bridge (Node.js) ready');
Max.post(`Connecting to Flask server at ${API_HOST}:${API_PORT}`);

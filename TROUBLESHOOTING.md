# Quick Start Guide

## Current Issue: Chat Not Working

The chat is showing "Unable to connect to AI service" errors. This happens when:

1. **LM Studio is not running** - Most common cause
2. **LM Studio's local server is not started**
3. **Model is not loaded in LM Studio**
4. **Model is too slow and timing out**

## Quick Fix Options

### Option 1: Check LM Studio (Recommended)

1. Open **LM Studio**
2. Go to **Local Server** tab
3. Make sure server is **started** (should show "Running on port 1234")
4. Make sure a **model is loaded**

### Option 2: Use Faster Model

If responses are too slow:
1. In LM Studio, load a smaller model like:
   - **TinyLlama-1.1B** (fastest)
   - **Phi-2** (fast and good quality)
2. Restart backend server

### Option 3: Disable LLaMA Temporarily

If you just want to test the app without AI:

Edit `backend/server.py` line 124 and change:
```python
include_context = data.get('include_context', False)  # Disable context
```

Or add a simple fallback response when LM Studio fails.

## Current Setup Status

✅ Backend server: Running on port 5000
✅ Flutter app: Running on port 8080
❓ LM Studio: Status unknown - please check

## Test Commands

```bash
# Test backend health
curl http://localhost:5000/health

# Test LM Studio connection
curl http://localhost:5000/api/test-llm

# Test simple chat (will timeout if LM Studio not working)
curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"messages\": [{\"role\": \"user\", \"content\": \"hi\"}], \"include_context\": false}"
```

## Next Steps

1. **Verify LM Studio is running** with local server started
2. **Try a simpler/faster model** if responses are slow
3. **Check backend logs** for specific error messages
4. Consider using **cloud API** (like OpenAI) if local model is too slow

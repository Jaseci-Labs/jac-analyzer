import asyncio
import json
import websockets
import sys;

async def is_valid_json(data):
    try:
        json.loads(data)
        return None  # Indicates success, no error message
    except ValueError as e:
        return str(e)  # Return the error message
async def echo(websocket, path):
   async for message in websocket:
       error_message = await is_valid_json(message)
       if error_message is None:
           response = {"status": "success", "message": "Valid JSON"}
       else:
           response = {"status": "error", "message": f"Invalid JSON: {error_message}"}

       print(response,flush=True) # Send output to stdout
       await websocket.send(json.dumps(response))


async def main():
    async with websockets.serve(echo, "localhost", 51734):
        print("Child server listening on port 51734",flush=True)
        await asyncio.Future()  # run forever

asyncio.run(main())

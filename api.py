import aiohttp
import asyncio
from typing import List, Dict, Optional
import json

class OpGGAPI:
    def __init__(self):
        self.base_url = "https://mcp-api.op.gg/mcp"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_champion_counters(self, champion_name: str, lane: str = "mid") -> Dict:
        # JSON-RPC 2.0 format payload with corrected parameter names
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "lol-champion-analysis",
                "arguments": {
                    "champion": "ZED",  # Try title case instead of capitalize
                    "position": "MID"  # Changed from champion_position to position
                }
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot/1.0"
        }
        
        try:
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract and parse the inner JSON from the text field
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content']
                        if content and len(content) > 0 and 'text' in content[0]:
                            # Parse the JSON string inside the text field
                            inner_json_str = content[0]['text']
                            parsed_data = json.loads(inner_json_str)
                            
                            # Save the parsed JSON data to scrapped.json
                            with open('scrapped.json', 'w', encoding='utf-8') as f:
                                json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                            
                            print(f"Received data for {champion_name} in {lane} lane")
                            return parsed_data
                    
                    # Fallback: save raw data if structure is different
                    with open('scrapped.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    return data
        
        except aiohttp.ClientError as e:
            return {"error": f"Network error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    

# MCP Server integration
class MCPServer:
    def __init__(self):
        self.api = OpGGAPI()
    
    async def handle_get_counters(self, champion: str, lane: str = "mid") -> Dict:
        """MCP tool for getting champion counters"""
        async with self.api as api_client:
            result = await api_client.get_champion_counters(champion, lane)
            return result

# Usage example
async def get_zed_counters():
    """Get counterpicks for Zed"""
    mcp_server = MCPServer()
    
    # Get Zed counters in mid lane
    print("Fetching Zed counters from OP.GG MCP API...")
    counters = await mcp_server.handle_get_counters("zed", "mid")
    
    # Check if we got valid data and print analysis
    if counters and 'data' in counters and 'data' in counters['data']:
        print_weak_counters_analysis(counters)
        print_strong_counters_analysis(counters)
    else:
        print("No valid counter data received")
    
    return counters

def analyze_weak_counters(data):
    """Extract and analyze weak counters for the champion"""
    weak_counters = data['data']['data']['weak_counters']
    champions_metadata = data['localized_metadata']['champions']
    
    # Create a lookup dictionary for champion names
    champion_lookup = {champ['id']: champ['name'] for champ in champions_metadata}
    
    # Process weak counters
    counter_info = []
    for counter in weak_counters:
        champion_id, plays, wins, win_rate = counter
        champion_name = champion_lookup.get(champion_id, f"Unknown ({champion_id})")
        
        counter_info.append({
            'champion': champion_name,
            'champion_id': champion_id,
            'games_played': plays,
            'wins': wins,
            'win_rate': round(win_rate * 100, 2),  # Convert to percentage
            'losses': plays - wins
        })
    
    # Sort by win rate (ascending - worst matchups first)
    counter_info.sort(key=lambda x: x['win_rate'])
    
    return counter_info

def print_weak_counters_analysis(data):
    """Print formatted analysis of weak counters"""
    weak_counters = analyze_weak_counters(data)
    
    print(f"\n=== WEAK COUNTERS FOR {data['champion']} ===")
    print("Champions that are harder to play against (sorted by difficulty):\n")
    
    for i, counter in enumerate(weak_counters[:10], 1):  # Top 10 worst matchups
        print(f"{i:2d}. {counter['champion']:<15} - {counter['win_rate']:5.1f}% WR "
              f"({counter['wins']:,}W/{counter['losses']:,}L from {counter['games_played']:,} games)")
    
    return weak_counters

def analyze_strong_counters(data):
    """Extract and analyze strong counters for the champion (easy matchups)"""
    strong_counters = data['data']['data']['strong_counters']
    champions_metadata = data['localized_metadata']['champions']
    
    # Create a lookup dictionary for champion names
    champion_lookup = {champ['id']: champ['name'] for champ in champions_metadata}
    
    # Process strong counters
    counter_info = []
    for counter in strong_counters:
        champion_id, plays, wins, win_rate = counter
        champion_name = champion_lookup.get(champion_id, f"Unknown ({champion_id})")
        
        counter_info.append({
            'champion': champion_name,
            'champion_id': champion_id,
            'games_played': plays,
            'wins': wins,
            'win_rate': round(win_rate * 100, 2),  # Convert to percentage
            'losses': plays - wins
        })
    
    # Sort by win rate (descending - best matchups first)
    counter_info.sort(key=lambda x: x['win_rate'], reverse=True)
    
    return counter_info

def print_strong_counters_analysis(data):
    """Print formatted analysis of strong counters"""
    strong_counters = analyze_strong_counters(data)
    
    print(f"\n=== STRONG COUNTERS FOR {data['champion']} ===")
    print("Champions that are easier to play against (sorted by easiest):\n")
    
    for i, counter in enumerate(strong_counters[:10], 1):  # Top 10 best matchups
        print(f"{i:2d}. {counter['champion']:<15} - {counter['win_rate']:5.1f}% WR "
              f"({counter['wins']:,}W/{counter['losses']:,}L from {counter['games_played']:,} games)")
    
    return strong_counters

if __name__ == "__main__":
    # Run the example
    asyncio.run(get_zed_counters())
    
    # Uncomment to test multiple champions
    # asyncio.run(test_multiple_champions())
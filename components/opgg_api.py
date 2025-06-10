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
    
    async def get_champion_data(self, champion_name: str, lane: str = "mid") -> Dict:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "lol-champion-analysis",
                "arguments": {
                    "champion": champion_name,
                    "position": lane
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
                    
                    if 'result' in data and 'content' in data['result']:
                        content = data['result']['content']
                        if content and len(content) > 0 and 'text' in content[0]:
                            inner_json_str = content[0]['text']
                            parsed_data = json.loads(inner_json_str)
                            
                            # Save to file
                            #with open('scrapped.json', 'w', encoding='utf-8') as f:
                            #   json.dump(parsed_data, f, indent=2, ensure_ascii=False)
                            
                            return parsed_data
                    
                    return data
        
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            return {"error": f"API error: {str(e)}"}

class ChampionAnalyzer:
    def __init__(self, data: Dict):
        self.data = data
        self.champion_data = data['data']['data']
        self.metadata = data['localized_metadata']
        self.champion = data['champion']
        self.position = data['position']
        
        # Create lookup dictionaries
        self.item_lookup = {item['id']: item for item in self.metadata['items']}
        self.spell_lookup = {spell['id']: spell for spell in self.metadata['spells']}
        self.champion_lookup = {champ['id']: champ for champ in self.metadata['champions']}
        self.rune_lookup = {rune['id']: rune for rune in self.metadata['runes']}
        self.rune_page_lookup = {page['id']: page for page in self.metadata['rune_pages']}

    def get_basic_stats(self) -> Dict:
        """Get basic champion statistics"""
        summary = self.champion_data['summary']
        avg_stats = summary['average_stats']
        
        return {
            'champion': self.champion,
            'position': self.position,
            'champion_id': summary.get('0', 'Unknown'),
            'games_played': avg_stats.get('0', 0) or 0,
            'win_rate': avg_stats.get('1', 0) or 0,
            'pick_rate': avg_stats.get('2', 0) or 0,
            'ban_rate': avg_stats.get('3', 0) or 0,
            'kda': avg_stats.get('4', 0) or 0,
            'tier': avg_stats.get('5', 'Unknown') or 'Unknown',
            'rank': avg_stats.get('6', 0) or 0
        }

    def get_position_stats(self) -> List[Dict]:
        """Get position-specific statistics"""
        positions = []
        for pos in self.champion_data['summary'].get('positions', []):
            pos_stats = pos.get('stats', {})
            tier_data = pos_stats.get('tier_data', [None, None])
            positions.append({
                'lane': pos.get('0', 'Unknown'),
                'games': pos_stats.get('0', 0) or 0,
                'win_rate': pos_stats.get('1', 0) or 0,
                'pick_rate': pos_stats.get('2', 0) or 0,
                'role_rate': pos_stats.get('3', 0) or 0,
                'ban_rate': pos_stats.get('4', 0) or 0,
                'kda': pos_stats.get('5', 0) or 0,
                'tier': tier_data[0] if len(tier_data) > 0 and tier_data[0] else 'Unknown',
                'rank': tier_data[1] if len(tier_data) > 1 and tier_data[1] else 0
            })
        return positions
    
    def get_game_length_performance(self) -> List[Dict]:
        """Get performance by game length"""
        performance = []
        for game_length in self.champion_data.get('game_lengths', []):
            if not game_length or len(game_length) < 4:
                continue
            try:
                length_range = f"{game_length[0]}-{game_length[0]+5}" if game_length[0] and game_length[0] > 0 else "0-25"
                performance.append({
                    'game_length': length_range,
                    'win_rate': game_length[1] or 0,
                    'rank': game_length[3] or 0
                })
            except (IndexError, TypeError):
                continue
        return performance

    def get_trends(self) -> Dict:
        """Get performance trends"""
        trends = self.champion_data.get('trends', {})
        win_history = []
        
        for patch_data in trends.get('win', [])[:5]:
            if not patch_data or len(patch_data) < 4:
                continue
            try:
                patch, wr, rank, date = patch_data
                win_history.append({
                    'patch': patch or 'Unknown',
                    'win_rate': wr or 0,
                    'rank': rank or 0,
                    'date': date or 'Unknown'
                })
            except (ValueError, TypeError):
                continue
        
        return {
            'overall_rank': trends.get('0', 0) or 0,
            'position_rank': trends.get('1', 0) or 0,
            'win_history': win_history
        }

    def get_summoner_spells(self) -> List[Dict]:
        """Get recommended summoner spells"""
        spells = []
        for spell_combo in self.champion_data.get('summoner_spells', [])[:5]:
            if not spell_combo or 'ids' not in spell_combo:
                continue
            try:
                spell_names = [self.spell_lookup.get(spell_id, {}).get('name', 'Unknown') for spell_id in spell_combo.get('ids', [])]
                wins = spell_combo.get('0', 0) or 0
                games = spell_combo.get('1', 0) or 0
                win_rate = wins / games if games > 0 else 0
                spells.append({
                    'spells': spell_names,
                    'wins': wins,
                    'games': games,
                    'pick_rate': spell_combo.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError):
                continue
        return spells
    
    def get_rune_pages(self) -> List[Dict]:
        """Get recommended rune pages"""
        runes = []
        for rune_page in self.champion_data.get('rune_pages', [])[:3]:
            if not rune_page:
                continue
            try:
                wins = rune_page.get('4', 0) or 0
                games = rune_page.get('3', 0) or 0
                win_rate = wins / games if games > 0 else 0
                primary_page = self.rune_page_lookup.get(rune_page.get('1'), {}).get('name', 'Unknown')
                secondary_page = self.rune_page_lookup.get(rune_page.get('2'), {}).get('name', 'Unknown')
                runes.append({
                    'primary': primary_page,
                    'secondary': secondary_page,
                    'games': games,
                    'wins': wins,
                    'pick_rate': rune_page.get('5', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError):
                continue
        return runes

    def get_runes(self) -> List[Dict]:
        """Get individual rune builds (not just pages)"""
        runes = []
        for rune in self.champion_data['runes'][:5]:
            primary_page = self.rune_page_lookup[rune['1']]['name']
            secondary_page = self.rune_page_lookup[rune['2']]['name']
            
            # Parse primary runes
            primary_runes = [self.rune_lookup[rune_id]['name'] for rune_id in rune['primary_rune_ids']]
            secondary_runes = [self.rune_lookup[rune_id]['name'] for rune_id in rune['secondary_rune_ids']]
            
            wins = rune['4']
            games = rune['3']
            win_rate = wins / games if games > 0 else 0
            
            runes.append({
                'primary_page': primary_page,
                'secondary_page': secondary_page,
                'primary_runes': primary_runes,
                'secondary_runes': secondary_runes,
                'games': games,
                'wins': wins,
                'pick_rate': rune['5'],
                'win_rate': win_rate
            })
        return runes

    def get_skill_masteries(self) -> List[Dict]:
        """Get skill masteries (priority order)"""
        masteries = []
        for mastery in self.champion_data['skill_masteries'][:3]:
            wins = mastery['1']
            games = mastery['0']
            win_rate = wins / games if games > 0 else 0
            masteries.append({
                'skill_priority': mastery['ids'],  # e.g., ['Q', 'E', 'W']
                'games': games,
                'wins': wins,
                'pick_rate': mastery['2'],
                'win_rate': win_rate
            })
        return masteries
    
    def get_skill_orders(self) -> List[Dict]:
        """Get skill leveling orders"""
        skills = []
        for skill_order in self.champion_data.get('skills', [])[:3]:
            if not skill_order or 'order' not in skill_order:
                continue
            try:
                wins = skill_order.get('1', 0) or 0
                games = skill_order.get('0', 0) or 0
                win_rate = wins / games if games > 0 else 0
                skills.append({
                    'order': skill_order.get('order', []),
                    'games': games,
                    'wins': wins,
                    'pick_rate': skill_order.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError):
                continue
        return skills

    def get_core_items(self) -> List[Dict]:
        """Get core item builds"""
        items = []
        for item_combo in self.champion_data.get('core_items', [])[:5]:
            if not item_combo or 'ids' not in item_combo:
                continue
            try:
                item_names = [self.item_lookup.get(item_id, {}).get('name', 'Unknown') for item_id in item_combo.get('ids', [])]
                wins = item_combo.get('1', 0) or 0
                games = item_combo.get('0', 0) or 0
                win_rate = wins / games if games > 0 else 0
                items.append({
                    'items': item_names,
                    'games': games,
                    'wins': wins,
                    'pick_rate': item_combo.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError):
                continue
        return items

    def get_boots(self) -> List[Dict]:
        """Get recommended boots"""
        boots = []
        for boot in self.champion_data.get('boots', [])[:3]:
            if not boot or 'ids' not in boot or not boot['ids']:
                continue
            try:
                boot_name = self.item_lookup.get(boot['ids'][0], {}).get('name', 'Unknown')
                wins = boot.get('1', 0) or 0
                games = boot.get('0', 0) or 0
                win_rate = wins / games if games > 0 else 0
                boots.append({
                    'boot': boot_name,
                    'games': games,
                    'wins': wins,
                    'pick_rate': boot.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError, IndexError):
                continue
        return boots

    def get_starter_items(self) -> List[Dict]:
        """Get starter item builds"""
        starters = []
        for starter in self.champion_data.get('starter_items', [])[:3]:
            if not starter or 'ids' not in starter:
                continue
            try:
                starter_names = [self.item_lookup.get(item_id, {}).get('name', 'Unknown') for item_id in starter.get('ids', [])]
                wins = starter.get('1', 0) or 0
                games = starter.get('0', 0) or 0
                win_rate = wins / games if games > 0 else 0
                starters.append({
                    'items': starter_names,
                    'games': games,
                    'wins': wins,
                    'pick_rate': starter.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError):
                continue
        return starters

    def get_final_items(self) -> List[Dict]:
        """Get popular final items"""
        items = []
        for item in self.champion_data.get('last_items', [])[:5]:
            if not item or 'ids' not in item or not item['ids']:
                continue
            try:
                item_name = self.item_lookup.get(item['ids'][0], {}).get('name', 'Unknown')
                wins = item.get('1', 0) or 0
                games = item.get('0', 0) or 0
                win_rate = wins / games if games > 0 else 0
                items.append({
                    'item': item_name,
                    'games': games,
                    'wins': wins,
                    'pick_rate': item.get('2', 0) or 0,
                    'win_rate': win_rate
                })
            except (KeyError, TypeError, IndexError):
                continue
        return items

    def get_weak_counters(self) -> List[Dict]:
        """Get champions that counter this champion"""
        counters = []
        for counter in self.champion_data.get('weak_counters', []):
            if not counter or len(counter) < 4:
                continue
            try:
                champion_id, plays, wins, win_rate = counter
                if plays is None or wins is None or win_rate is None:
                    continue
                    
                champion_name = self.champion_lookup.get(champion_id, f"Unknown ({champion_id})")
                if isinstance(champion_name, dict) and 'name' in champion_name:
                    champion_name = champion_name['name']
                
                counters.append({
                    'champion': champion_name,
                    'games_played': plays,
                    'wins': wins,
                    'losses': plays - wins,
                    'win_rate': win_rate
                })
            except (ValueError, TypeError):
                continue
        
        counters.sort(key=lambda x: x['win_rate'])
        return counters

    def get_strong_counters(self) -> List[Dict]:
        """Get champions this champion counters"""
        counters = []
        for counter in self.champion_data.get('strong_counters', []):
            if not counter or len(counter) < 4:
                continue
            try:
                champion_id, plays, wins, win_rate = counter
                if plays is None or wins is None or win_rate is None:
                    continue
                    
                champion_name = self.champion_lookup.get(champion_id, f"Unknown ({champion_id})")
                if isinstance(champion_name, dict) and 'name' in champion_name:
                    champion_name = champion_name['name']
                    
                counters.append({
                    'champion': champion_name,
                    'games_played': plays,
                    'wins': wins,
                    'losses': plays - wins,
                    'win_rate': win_rate
                })
            except (ValueError, TypeError):
                continue
        
        counters.sort(key=lambda x: x['win_rate'], reverse=True)
        return counters

def print_basic_stats(stats: Dict):
    """Print basic statistics"""
    print(f"\n=== {stats['champion']} {stats['position']} BASIC STATS ===")
    print(f"Games Played: {stats['games_played']:,}")
    print(f"Win Rate: {stats['win_rate']*100:.2f}%")
    print(f"Pick Rate: {stats['pick_rate']*100:.2f}%")
    print(f"Ban Rate: {stats['ban_rate']*100:.2f}%")
    print(f"Average KDA: {stats['kda']:.2f}")
    print(f"Tier: {stats['tier']} | Rank: {stats['rank']}")

def print_summoner_spells(spells: List[Dict]):
    """Print summoner spells"""
    print(f"\n=== SUMMONER SPELLS ===")
    for i, spell in enumerate(spells, 1):
        print(f"{i}. {' + '.join(spell['spells'])} - {spell['pick_rate']*100:.1f}% pick rate "
              f"({spell['wins']:,}W/{spell['games']:,} games)")

def print_core_items(items: List[Dict]):
    """Print core items"""
    print(f"\n=== CORE ITEMS ===")
    for i, item in enumerate(items, 1):
        print(f"{i}. {' + '.join(item['items'])} - {item['pick_rate']*100:.1f}% pick rate "
              f"({item['wins']:,}W/{item['games']:,} games)")

def print_boots(boots: List[Dict]):
    """Print boots"""
    print(f"\n=== BOOTS ===")
    for i, boot in enumerate(boots, 1):
        print(f"{i}. {boot['boot']} - {boot['pick_rate']*100:.1f}% pick rate "
              f"({boot['wins']:,}W/{boot['games']:,} games)")

def print_starter_items(starters: List[Dict]):
    """Print starter items"""
    print(f"\n=== STARTER ITEMS ===")
    for i, starter in enumerate(starters, 1):
        print(f"{i}. {' + '.join(starter['items'])} - {starter['pick_rate']*100:.1f}% pick rate "
              f"({starter['wins']:,}W/{starter['games']:,} games)")

def print_final_items(items: List[Dict]):
    """Print final items"""
    print(f"\n=== FINAL ITEMS ===")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['item']} - {item['pick_rate']*100:.1f}% pick rate "
              f"({item['wins']:,}W/{item['games']:,} games)")

def print_rune_pages(rune_pages: List[Dict]):
    """Print rune pages"""
    print(f"\n=== RUNE PAGES ===")
    for i, rune in enumerate(rune_pages, 1):
        print(f"{i}. {rune['primary']} + {rune['secondary']} - {rune['pick_rate']*100:.1f}% pick rate "
              f"({rune['wins']:,}W/{rune['games']:,} games)")

def print_runes(runes: List[Dict]):
    """Print detailed runes"""
    print(f"\n=== DETAILED RUNES ===")
    for i, rune in enumerate(runes, 1):
        print(f"\n{i}. {rune['primary_page']} + {rune['secondary_page']} - {rune['pick_rate']*100:.1f}% pick rate")
        print(f"   Primary: {' > '.join(rune['primary_runes'])}")
        print(f"   Secondary: {' + '.join(rune['secondary_runes'])}")
        print(f"   ({rune['wins']:,}W/{rune['games']:,} games)")

def print_skill_orders(skills: List[Dict]):
    """Print skill orders"""
    print(f"\n=== SKILL ORDERS ===")
    for i, skill in enumerate(skills, 1):
        print(f"{i}. {' > '.join(skill['order'])} - {skill['pick_rate']*100:.1f}% pick rate "
              f"({skill['wins']:,}W/{skill['games']:,} games)")

def print_skill_masteries(masteries: List[Dict]):
    """Print skill masteries"""
    print(f"\n=== SKILL MASTERIES ===")
    for i, mastery in enumerate(masteries, 1):
        print(f"{i}. {' > '.join(mastery['skill_priority'])} priority - {mastery['pick_rate']*100:.1f}% pick rate "
              f"({mastery['wins']:,}W/{mastery['games']:,} games)")

def print_position_stats(positions: List[Dict]):
    """Print position statistics"""
    print(f"\n=== POSITION STATS ===")
    for pos in positions:
        print(f"\n{pos['lane']} Lane:")
        print(f"  Games: {pos['games']:,} | WR: {pos['win_rate']*100:.2f}%")
        print(f"  Pick Rate: {pos['pick_rate']*100:.2f}% | Role Rate: {pos['role_rate']*100:.2f}%")
        print(f"  Ban Rate: {pos['ban_rate']*100:.2f}% | KDA: {pos['kda']:.2f}")
        print(f"  Tier: {pos['tier']} | Rank: {pos['rank']}")

def print_game_length_performance(performance: List[Dict]):
    """Print game length performance"""
    print(f"\n=== GAME LENGTH PERFORMANCE ===")
    for perf in performance:
        print(f"{perf['game_length']} min: {perf['win_rate']*100:.1f}% WR (Rank #{perf['rank']})")

def print_trends(trends: Dict):
    """Print performance trends"""
    print(f"\n=== PERFORMANCE TRENDS ===")
    print(f"Overall Rank: #{trends['overall_rank']} | Position Rank: #{trends['position_rank']}")
    print("Recent Win Rate History:")
    for patch_data in trends['win_history']:
        print(f"  Patch {patch_data['patch']}: {patch_data['win_rate']*100:.1f}% WR (Rank #{patch_data['rank']})")

def print_weak_counters(counters: List[Dict]):
    """Print weak counters"""
    print(f"\n=== WEAK COUNTERS (Hardest Matchups) ===")
    for i, counter in enumerate(counters[:10], 1):
        champion_name = str(counter['champion'])  # Ensure it's a string
        print(f"{i:2d}. {champion_name:<15} - {counter['win_rate']*100:5.1f}% WR "
              f"({counter['wins']:,}W/{counter['losses']:,}L from {counter['games_played']:,} games)")
        
def print_strong_counters(counters: List[Dict]):
    """Print strong counters"""
    print(f"\n=== STRONG COUNTERS (Easiest Matchups) ===")
    for i, counter in enumerate(counters[:10], 1):
        champion_name = str(counter['champion'])  # Ensure it's a string
        print(f"{i:2d}. {champion_name:<15} - {counter['win_rate']*100:5.1f}% WR "
              f"({counter['wins']:,}W/{counter['losses']:,}L from {counter['games_played']:,} games)")

async def analyze_champion(champion: str, lane: str = "mid"):
    """Main function to analyze a champion"""
    print(f"Fetching {champion} data from OP.GG API...")
    
    async with OpGGAPI() as api:
        data = await api.get_champion_data(champion.upper(), lane.upper())
        
        if 'error' in data:
            print(f"Error: {data['error']}")
            return
        
        if 'data' not in data or 'data' not in data['data']:
            print("No valid data received")
            return
        
        # Create analyzer
        analyzer = ChampionAnalyzer(data)
        
        # Get and print ALL stats
        print("="*60)
        print(f"COMPLETE ANALYSIS FOR {champion.upper()} {lane.upper()}")
        print("="*60)
        
        # Basic stats
        basic_stats = analyzer.get_basic_stats()
        print_basic_stats(basic_stats)
        
        # Position stats
        position_stats = analyzer.get_position_stats()
        print_position_stats(position_stats)
        
        # Summoner spells
        summoner_spells = analyzer.get_summoner_spells()
        print_summoner_spells(summoner_spells)
        
        # Items
        core_items = analyzer.get_core_items()
        print_core_items(core_items)
        
        boots = analyzer.get_boots()
        print_boots(boots)
        
        starter_items = analyzer.get_starter_items()
        print_starter_items(starter_items)
        
        final_items = analyzer.get_final_items()
        print_final_items(final_items)
        
        # Runes
        rune_pages = analyzer.get_rune_pages()
        print_rune_pages(rune_pages)
        
        runes = analyzer.get_runes()
        print_runes(runes)
        
        # Skills
        skill_masteries = analyzer.get_skill_masteries()
        print_skill_masteries(skill_masteries)
        
        skill_orders = analyzer.get_skill_orders()
        print_skill_orders(skill_orders)
        
        # Performance metrics
        game_length_performance = analyzer.get_game_length_performance()
        print_game_length_performance(game_length_performance)
        
        trends = analyzer.get_trends()
        print_trends(trends)
        
        # Counters
        weak_counters = analyzer.get_weak_counters()
        print_weak_counters(weak_counters)
        
        strong_counters = analyzer.get_strong_counters()
        print_strong_counters(strong_counters)
        
        print("="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        return analyzer

if __name__ == "__main__":
    # test api
    asyncio.run(analyze_champion("zed", "mid"))
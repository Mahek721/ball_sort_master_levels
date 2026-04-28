import json
import random
import os
import re
from datetime import datetime

# Configuration
LEVELS_DIR = "generate_levels/levels"
LIST_FILE = "generate_levels/levels-list.json"
BATCH_SIZE = 10  # Number of levels to generate per run
COLORS = [
    "#FF3B30", "#007AFF", "#34C759", "#FF9500", "#AF52DE", 
    "#5AC8FA", "#FFCC00", "#FF2D55", "#5856D6", "#8E8E93",
    "#1D1D1F", "#00C7BE", "#32ADE6", "#64D2FF", "#0040DD",
    "#FF375F", "#BF5AF2", "#FF9F0A", "#30D158", "#0A84FF"
]

def generate_level(level_num):
    # Scale complexity: more colors every 5 levels
    num_colors = 3 + (level_num // 5)
    num_colors = min(num_colors, len(COLORS))
    
    # Empty tubes: starts at 2, increases to 3 for harder levels
    num_empty = 2 if level_num < 40 else 3
    
    total_tubes = num_colors + num_empty
    
    # Tube capacities
    capacities = [4] * total_tubes
    
    # Introduce small tubes (capacity 3) for higher challenge
    if level_num > 15:
        num_small = min(3, 1 + (level_num // 20))
        small_indices = random.sample(range(total_tubes), num_small)
        for idx in small_indices:
            capacities[idx] = 3
            
    # Safety: ensure total capacity can hold all balls
    while sum(capacities) < (num_colors * 4):
        idx = random.randint(0, total_tubes - 1)
        if capacities[idx] < 4:
            capacities[idx] += 1

    # Start with solved state
    tubes = [[] for _ in range(total_tubes)]
    for i in range(num_colors):
        tubes[i] = [COLORS[i]] * 4
    
    # Scatter phase (Backward shuffle)
    # The more moves, the more mixed the balls become
    num_moves = 80 + (level_num * 8)
    for _ in range(num_moves):
        non_empty = [i for i, t in enumerate(tubes) if t]
        if not non_empty: break
        
        src_idx = random.choice(non_empty)
        
        has_space = [i for i, t in enumerate(tubes) if len(t) < capacities[i] and i != src_idx]
        if not has_space: continue
        
        target_idx = random.choice(has_space)
        
        ball = tubes[src_idx].pop()
        tubes[target_idx].append(ball)
    
    return {
        "level": level_num,
        "tubes": tubes,
        "capacities": capacities
    }

def get_last_level_number():
    if not os.path.exists(LEVELS_DIR):
        return 0
    files = os.listdir(LEVELS_DIR)
    level_nums = []
    for f in files:
        # Support both underscore and hyphen during transition
        match = re.search(r'level[_-](\d+)\.json', f)
        if match:
            level_nums.append(int(match.group(1)))
    return max(level_nums) if level_nums else 0

def update_levels_list():
    if not os.path.exists(LEVELS_DIR):
        return
    
    # Move/Rename old files if any
    files = os.listdir(LEVELS_DIR)
    for f in files:
        if f.startswith('level_') and f.endswith('.json'):
            old_path = os.path.join(LEVELS_DIR, f)
            new_name = f.replace('_', '-')
            new_path = os.path.join(LEVELS_DIR, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed {f} to {new_name}")

    # Re-scan for hyphenated files
    files = [f for f in os.listdir(LEVELS_DIR) if f.endswith('.json') and f.startswith('level-')]
    levels = []
    
    for f in sorted(files, key=lambda x: int(re.search(r'level-(\d+)\.json', x).group(1))):
        level_num = int(re.search(r'level-(\d+)\.json', f).group(1))
        levels.append({
            "id": level_num,
            "path": f"generate_levels/levels/{f}",
            "difficulty": "Easy" if level_num <= 10 else "Medium" if level_num <= 25 else "Hard"
        })
    
    data = {
        "total_levels": len(levels),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "levels": levels
    }
    
    with open(LIST_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Successfully updated {LIST_FILE} with {len(levels)} levels.")

def main():
    if not os.path.exists(LEVELS_DIR):
        os.makedirs(LEVELS_DIR)
        
    start_level = get_last_level_number() + 1
    end_level = start_level + BATCH_SIZE - 1
    
    if start_level > 1:
        print(f"Current last level: {start_level - 1}")
    
    # Only generate if called directly or if list is missing
    # But usually we want to update the list even if no new levels are generated
    
    # Check if we should generate new levels (optional, but keep it for convenience)
    # For now, let's just make sure we can trigger generation if needed.
    # If the user just wants the list, they can run simple update.
    
    # For the first time, let's update everything.
    update_levels_list()

if __name__ == "__main__":
    main()

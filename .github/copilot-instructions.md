# Copilot Instructions for Kreatures

## Project Overview
Kreatures is a virtual creature simulation game written in Python where creatures interact in a shared environment. Players create a creature and observe how it interacts with other creatures through fighting, befriending, and reproduction. This project was originally created in 2017 as a learning exercise and represents the foundational ideas later expanded in the Interakt and Apex projects.

## Architecture
The project follows a modular object-oriented design:

- **Core Game Loop** (`src/kreatures.py`): Main game class that manages the simulation, entity interactions, and game flow
- **World Management** (`src/world/world.py`): Manages the virtual environment and entity collection
- **Living Entities** (`src/entity/livingEntity.py`): Creature behavior, actions (fight, befriend, reproduce), and relationship management
- **Configuration** (`src/config/config.py`): Game settings like god mode, tick limits, and timing
- **Statistics** (`src/stats/stats.py`): Tracks creature performance metrics
- **Flags** (`src/flags/flags.py`): Behavioral modifiers and adjustment parameters

## Key Game Mechanics
1. **Creature Interactions**: Each tick, creatures randomly interact with others through:
   - Fighting (removes target from world)
   - Befriending (adds to friends list, prevents future fighting)
   - Reproduction (creates child entities with both parents)
   
2. **Dynamic Behavior**: Creatures adjust their behavioral tendencies based on actions:
   - More fighting increases `chanceToFight`, decreases `chanceToBefriend`
   - More befriending increases `chanceToBefriend`, decreases `chanceToFight`

3. **Parent-Child Relationships**: New creatures track their parents and children, allowing for generational gameplay

## Coding Standards
- **Indentation**: Use tabs (not spaces) to match existing codebase
- **Naming**: 
  - Classes: PascalCase (e.g., `LivingEntity`)
  - Methods/variables: camelCase (e.g., `getNextAction`)
  - Constants: snake_case or camelCase depending on context
- **Comments**: Include copyright headers and author annotations where appropriate
- **String Formatting**: Use % formatting for consistency with existing code

## File Structure Guidelines
- Keep modules in their respective directories under `src/`
- Each module should have an `__init__.py` file
- Maintain the existing package structure:
  ```
  src/
  ├── config/
  ├── entity/
  ├── flags/
  ├── stats/
  ├── world/
  └── kreatures.py (main entry point)
  ```

## Development Workflow
- **Formatting**: Use `./format.sh` (runs black and autoflake)
- **Testing**: Use `./test.sh` (runs pytest with coverage)
- **Running**: Use `./run.sh` or directly `python src/kreatures.py`

## Testing Approach
- The project expects pytest for testing
- Tests should cover core game mechanics and entity interactions
- Use coverage reporting via pytest-cov

## Important Implementation Notes
1. **Entity Management**: Always use World methods to add/remove entities to maintain consistency
2. **Random Behavior**: The simulation relies heavily on random number generation for creature decisions
3. **Relationship Tracking**: When creating relationships (friends, parents, children), ensure bidirectional updates
4. **God Mode**: Player creature can be protected from being eaten when `config.godMode` is enabled
5. **Simulation Limits**: Respect `maxTicks` and `tickLength` from configuration

## Common Patterns
- Entity actions return string identifiers ("fight", "befriend", "love", "nothing")
- Log entries use % string formatting for creature interactions
- Statistics are updated immediately when actions occur
- Parent-child relationships are established through dedicated methods

## Error Handling
- Handle empty entity lists gracefully
- Validate entity existence before operations
- Ensure random selections don't fail on edge cases

## Performance Considerations
- The simulation runs in real-time with configurable tick lengths
- Entity interactions are O(n²) per tick, so consider performance with large populations
- Memory usage grows with creature logs and relationship tracking

## Legacy Code Considerations
- This is a learning project from 2017, so some patterns may be dated
- Maintain backward compatibility when making improvements
- Preserve the original game feel and mechanics
- Tab indentation and existing naming conventions should be respected
from components import *
from ecs_types import EntityId, System
import pygame
import settings
from sound_engine import SoundEngine
from .grid_movement_system import GridMovementSystem


class InputSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, PlayerTag]
    
    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        grid_position, _ = components
        
        movement_system = ecs.get_system(GridMovementSystem)
        if not movement_system:
            return
            
        events = ecs.get_variable('events')
        if not events:
            return

        turn_component = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_component = turn
            break

        if not turn_component or not turn_component.is_player_turn:
            return

        enemy_positions: dict[tuple[int, int], EntityId] = {}
        for e_id, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
            enemy_positions[(enemy_grid_pos.x, enemy_grid_pos.y)] = e_id

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    import sys
                    sys.exit()
                    
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = 1
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = 1

                if event.key == pygame.K_g:
                    self._handle_item_pickup(entity_id, grid_position, ecs)
                    continue

                if event.key == pygame.K_h:
                    self._handle_health_potion(entity_id, ecs)
                    continue

                if event.key == pygame.K_b:
                    self._handle_bomb_placement(entity_id, grid_position, turn_component, ecs)
                    continue

                if dx != 0 or dy != 0:
                    self._handle_movement(entity_id, grid_position, dx, dy, enemy_positions, movement_system, turn_component, ecs)

    def _handle_item_pickup(self, entity_id: EntityId, grid_position: GridPosition, ecs):
        for item_id, (item_comp, _) in ecs.get_entities_with_components(Item, GridPosition):
            item_grid = ecs.get_component(item_id, GridPosition)
            if item_grid and item_grid.x == grid_position.x and item_grid.y == grid_position.y:
                inv = ecs.get_component(entity_id, Inventory)
                rend = ecs.get_component(item_id, Render)
                if inv and rend and len(inv.items) < inv.capacity:
                    inv.items.append(InventoryItem(name=item_comp.name, sprite=rend.sprite))
                    ecs.remove_entity(item_id)
                break

    def _handle_health_potion(self, entity_id: EntityId, ecs):
        inv = ecs.get_component(entity_id, Inventory)
        player_health = ecs.get_component(entity_id, Health)
        if inv and player_health:
            for inv_item in inv.items:
                if inv_item.name == 'Health Potion' and player_health.amount < player_health.max_amount:
                    player_health.amount = min(player_health.max_amount, player_health.amount + 30)
                    inv.items.remove(inv_item)
                    try:
                        SoundEngine.get().play('heal_potion', volume=0.6)
                    except RuntimeError:
                        pass
                    break

    def _handle_bomb_placement(self, entity_id: EntityId, grid_position: GridPosition, turn_component: TurnComponent, ecs):
        inv = ecs.get_component(entity_id, Inventory)
        if inv:
            for inv_item in inv.items:
                if inv_item.name == 'Bomb':
                    occupied = False
                    for _, (b_grid_pos, __) in ecs.get_entities_with_components(GridPosition, Bomb):
                        if b_grid_pos.x == grid_position.x and b_grid_pos.y == grid_position.y:
                            occupied = True
                            break
                    if occupied:
                        print("В этой клетке уже есть бомба!")
                        break

                    enemy_in_cell = False
                    for _, (e_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
                        if e_grid_pos.x == grid_position.x and e_grid_pos.y == grid_position.y:
                            enemy_in_cell = True
                            break
                    if enemy_in_cell:
                        print("Нельзя поставить бомбу на клетку с врагом!")
                        break

                    sprite = inv_item.sprite
                    turn_count = turn_component.turn_count if turn_component else 0
                    
                    try:
                        new_bomb_id = ecs.create_entity([
                            Position(position=pygame.Vector2(grid_position.x * settings.TileMap.TILE_SIZE,
                                                             grid_position.y * settings.TileMap.TILE_SIZE)),
                            GridPosition(x=grid_position.x, y=grid_position.y),
                            Render(sprite=sprite, scale=1.0, layer=2),
                            Bomb(planted_turn=turn_count, fuse_turns=3, radius=1, damage=25)
                        ])
                        
                        if new_bomb_id is not None:
                            inv.items.remove(inv_item)
                            print("Бомба установлена!")
                        else:
                            print("Ошибка создания бомбы!")
                    except Exception as e:
                        print(f"Ошибка при создании бомбы: {e}")
                    break

    def _handle_movement(self, entity_id: EntityId, grid_position: GridPosition, dx: int, dy: int, 
                        enemy_positions: dict, movement_system, turn_component: TurnComponent, ecs):
        new_x, new_y = grid_position.x + dx, grid_position.y + dy
        action_performed = False
        
        if (new_x, new_y) in enemy_positions:
            enemy_id = enemy_positions[(new_x, new_y)]
            player_attack = ecs.get_component(entity_id, Attack)
            enemy_health = ecs.get_component(enemy_id, Health)
            if player_attack and enemy_health:
                enemy_health.apply_damage(player_attack.damage)
                try:
                    SoundEngine.get().play('player_attack', volume=0.6)
                except RuntimeError:
                    pass
                action_performed = True
        elif movement_system.is_walkable(new_x, new_y, ecs):
            grid_position.x = new_x
            grid_position.y = new_y
            action_performed = True

            try:
                SoundEngine.get().play('footstep', volume=0.4)
            except RuntimeError:
                pass

        if action_performed:
            turn_component.turn_count += 1
            turn_component.player_moved = True

            enemies_to_move = 0
            for e_id, _ in ecs.get_entities_with_components(EnemyTag):
                is_flying_e = ecs.get_component(e_id, FlyingEnemyTag) is not None
                if (turn_component.turn_count % 2 == 0) or is_flying_e:
                    enemies_to_move += 1
                    break

            if enemies_to_move > 0:
                turn_component.is_player_turn = False
            else:
                turn_component.is_player_turn = True 
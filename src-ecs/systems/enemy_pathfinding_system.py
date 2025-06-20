from components import *
from entity_component_system import EntityComponentSystem
from ecs_types import EntityId, System
import pygame
import debug
import settings
from pathfinding import AStar
from sound_engine import SoundEngine


class EnemyPathfindingSystem(System):
    def __init__(self):
        super().__init__()
        self.required_components = [GridPosition, EnemyTag]
        self.pathfinder = AStar()
        self.current_paths = {}
        self.enemies_moved = 0

    def update(self, entity_id: EntityId, components: list[Component], ecs=None):
        turn_component = None
        for _, (turn,) in ecs.get_entities_with_components(TurnComponent):
            turn_component = turn
            break

        if not turn_component or turn_component.is_player_turn:
            return

        is_flying_enemy = ecs.get_component(entity_id, FlyingEnemyTag) is not None
        odd_turn = (turn_component.turn_count % 2 != 0)

        if odd_turn and not is_flying_enemy:
            return

        grid_position, _ = components
        
        player_pos = None
        for _, (player_grid_pos, _) in ecs.get_entities_with_components(GridPosition, PlayerTag):
            player_pos = (player_grid_pos.x, player_grid_pos.y)
            break
            
        if not player_pos:
            return

        walkable_tiles = set()
        for _, (tile_grid_pos, tile) in ecs.get_entities_with_components(GridPosition, TileComponent):
            if tile.walkable:
                walkable_tiles.add((tile_grid_pos.x, tile_grid_pos.y))

        enemy_positions = set()
        for enemy_id, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
            if enemy_id != entity_id:
                enemy_positions.add((enemy_grid_pos.x, enemy_grid_pos.y))

        walkable_tiles = walkable_tiles - enemy_positions

        current_pos = (grid_position.x, grid_position.y)
        path = self.pathfinder.find_path(current_pos, player_pos, walkable_tiles)[:-1]
        
        self.current_paths[entity_id] = path
        
        is_wizard = ecs.get_component(entity_id, WizardTag) is not None
        if is_wizard:
            self._handle_wizard_behavior(entity_id, grid_position, player_pos, path, turn_component, walkable_tiles, enemy_positions, ecs)
            return

        self._handle_general_enemy_movement(entity_id, grid_position, path, turn_component, ecs)

    def _handle_wizard_behavior(self, entity_id: EntityId, grid_position: GridPosition, player_pos: tuple, 
                               path: list, turn_component: TurnComponent, walkable_tiles: set, enemy_positions: set, ecs):
        w_state: WizardState | None = ecs.get_component(entity_id, WizardState)
        if w_state is None:
            w_state = WizardState()
            ecs._components[WizardState][entity_id] = w_state

        if turn_component.turn_count - w_state.last_shot_turn >= 4:
            self._create_fireball(grid_position, player_pos, turn_component, w_state, ecs)

        def cheb_dist(a: tuple[int, int], b: tuple[int, int]):
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

        current_pos = (grid_position.x, grid_position.y)
        cur_dist = cheb_dist(current_pos, player_pos)
        next_pos_candidate = path[1] if len(path) > 1 else current_pos
        next_dist = cheb_dist(next_pos_candidate, player_pos)

        if cur_dist < 4:
            best_pos = self._find_retreat_position(grid_position, player_pos, walkable_tiles, enemy_positions)
            if best_pos != current_pos:
                grid_position.x, grid_position.y = best_pos
                self._increment_enemy_counter(turn_component, ecs)
                return

        if next_dist < 3:
            self._increment_enemy_counter(turn_component, ecs)
            return

        self._handle_general_enemy_movement(entity_id, grid_position, path, turn_component, ecs)

    def _create_fireball(self, grid_position: GridPosition, player_pos: tuple, turn_component: TurnComponent, w_state: WizardState, ecs):
        wizard_pixel_x = grid_position.x * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
        wizard_pixel_y = grid_position.y * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
        player_pixel_x = player_pos[0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
        player_pixel_y = player_pos[1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2

        delta_x = player_pixel_x - wizard_pixel_x
        delta_y = player_pixel_y - wizard_pixel_y
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5

        if distance > 0:
            speed = 1.0
            velocity_x = (delta_x / distance) * speed
            velocity_y = (delta_y / distance) * speed

            assets = ecs.get_variable('render_target').assets if ecs.get_variable('render_target') else None
            sprite = None
            if assets:
                sprite = assets.get_sprite('Items/cookie.png')
            pos_px = pygame.Vector2(wizard_pixel_x, wizard_pixel_y)
            ecs.create_entity([
                Position(position=pos_px),
                Hitbox(offset_x=-4, offset_y=-4, width=8, height=8),
                Render(sprite=sprite, scale=1, layer=1),
                Fireball(velocity_x=velocity_x, velocity_y=velocity_y, damage=15)
            ])

            w_state.last_shot_turn = turn_component.turn_count

    def _find_retreat_position(self, grid_position: GridPosition, player_pos: tuple, walkable_tiles: set, enemy_positions: set):
        def cheb_dist(a: tuple[int, int], b: tuple[int, int]):
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
        
        current_pos = (grid_position.x, grid_position.y)
        best_pos = current_pos
        best_dist = cheb_dist(current_pos, player_pos)
        
        for dx_off in (-1, 0, 1):
            for dy_off in (-1, 0, 1):
                if dx_off == 0 and dy_off == 0:
                    continue
                cand = (grid_position.x + dx_off, grid_position.y + dy_off)
                if cand not in walkable_tiles or cand in enemy_positions:
                    continue
                d = cheb_dist(cand, player_pos)
                if d >= 3 and d > best_dist:
                    best_dist = d
                    best_pos = cand
        return best_pos

    def _handle_general_enemy_movement(self, entity_id: EntityId, grid_position: GridPosition, path: list, turn_component: TurnComponent, ecs):
        if len(path) == 1:
            self._attack_player(entity_id, ecs)
            self._increment_enemy_counter(turn_component, ecs)
            return

        if len(path) > 1:
            enemy_positions = set()
            for enemy_id, (enemy_grid_pos, _) in ecs.get_entities_with_components(GridPosition, EnemyTag):
                if enemy_id != entity_id:
                    enemy_positions.add((enemy_grid_pos.x, enemy_grid_pos.y))
            
            next_pos = path[1]
            if next_pos not in enemy_positions:
                grid_position.x, grid_position.y = next_pos
                self._increment_enemy_counter(turn_component, ecs)

        if len(path) <= 1:
            self._increment_enemy_counter(turn_component, ecs)

    def _attack_player(self, entity_id: EntityId, ecs):
        player_id = None
        for p_id, _ in ecs.get_entities_with_components(PlayerTag):
            player_id = p_id
            break
        if player_id is not None:
            enemy_attack = ecs.get_component(entity_id, Attack)
            player_health = ecs.get_component(player_id, Health)
            if enemy_attack and player_health:
                player_health.apply_damage(enemy_attack.damage)
                try:
                    SoundEngine.get().play('player_hurt', volume=0.7)
                except RuntimeError:
                    pass

    def _increment_enemy_counter(self, turn_component: TurnComponent, ecs):
        self.enemies_moved += 1
        total_enemies = 0
        for e_id, _ in ecs.get_entities_with_components(EnemyTag):
            is_flying_e = ecs.get_component(e_id, FlyingEnemyTag) is not None
            if (turn_component.turn_count % 2 == 0) or is_flying_e:
                total_enemies += 1

        if self.enemies_moved >= total_enemies:
            self.enemies_moved = 0
            turn_component.is_player_turn = True
            turn_component.player_moved = False

    def draw_debug(self, ecs: EntityComponentSystem):
        if not debug.IS_DEBUG:
            return

        render_target = ecs.get_variable('render_target')
        if not render_target or not render_target.surface:
            return

        for entity_id, path in self.current_paths.items():
            if not path:
                continue

            for i in range(len(path) - 1):
                start_pos = (
                    path[i][0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    path[i][1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                end_pos = (
                    path[i + 1][0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    path[i + 1][1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                pygame.draw.line(render_target.surface, pygame.Color('red'), start_pos, end_pos, 2)

            for point in path:
                center_pos = (
                    point[0] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2,
                    point[1] * settings.TileMap.TILE_SIZE + settings.TileMap.TILE_SIZE // 2
                )
                pygame.draw.circle(render_target.surface, pygame.Color('yellow'), center_pos, 3) 
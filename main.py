import pygame
import sys

WIDTH, HEIGHT = 1200, 800
FPS = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHT_RED = (255, 154, 152)
LIGHT_BLUE = (200, 200, 255)
LIGHT_YELLOW = (255, 255, 200)
GREEN = (144, 238, 144)
LIGHT_GREEN = (144, 238, 144)
CREAM = (255, 255, 200)

class Grid:
    def __init__(self, n):
        self.rows = n
        self.cols = n
        self.n = n
        
        self.cell_size = 800 // n
        self.center_offset = self.cell_size // 2
        self.grid_size = self.cell_size * n 
        self.grid_offset = (HEIGHT - self.grid_size) // 2

        self.default_colour = WHITE
        self.highlight_colour = LIGHT_YELLOW
        self.chosen_colour = GREEN
        self.colour = self.default_colour

        self.highlighted_square = None
        self.chosen_square = None
        self.invalid_square = None
        self.path = None
        
        self.index = 1
        self.font = pygame.font.Font(None, int(self.cell_size * 0.5))

        self.start_x = (HEIGHT - self.grid_size) // 2
        self.start_y = (HEIGHT - self.grid_size) // 2 

        knight_image = pygame.image.load("knight.png")
        self.knight_image = pygame.transform.scale(knight_image, (int(self.cell_size * 0.70), int(self.cell_size * 0.70)))
        self.knight_image_rect = self.knight_image.get_rect()

    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(
                    self.start_x + col * self.cell_size,
                    self.start_y + row * self.cell_size,
                    self.cell_size, self.cell_size)

                if (col, row) == self.highlighted_square:
                    self.colour = LIGHT_BLUE
                elif (row + col) % 2 == 0:
                    self.colour = LIGHT_GREEN
                else:
                    self.colour = CREAM
                
                pygame.draw.rect(screen, self.colour, rect, 0)  
                pygame.draw.rect(screen, BLACK, rect, 1)

    def draw_path(self, screen):
        path = self.path[:self.index + 1]

        if self.index >= self.n**2: 
            tx, ty = path[-1]
            tx, ty = self.start_x + (tx * self.cell_size), self.start_y + (ty * self.cell_size)
            rect = pygame.Rect(tx, ty, self.cell_size, self.cell_size)
            pygame.draw.rect(screen, LIGHT_RED, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            x1, y1 = self.start_x + x1 * self.cell_size + self.center_offset, self.start_y + y1 * self.cell_size + self.center_offset
            last_pos = x2, y2 = self.start_x + x2 * self.cell_size + self.center_offset, self.start_y + y2 * self.cell_size + self.center_offset

            if i == 0:
                rect = pygame.Rect(
                    x1 - self.center_offset,
                    y1 - self.center_offset,
                    self.cell_size, self.cell_size)
                pygame.draw.rect(screen, LIGHT_RED, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)

            pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 5)
            pygame.draw.circle(screen, RED, (x1, y1), 5)
            pygame.draw.circle(screen, RED, (x2, y2), 5)

            text_surface = self.font.render(str(i + 1), True, BLACK) 
            text_rect = text_surface.get_rect()
            text_rect.center = (x1, y1 - int(self.cell_size * 0.25))
            screen.blit(text_surface, text_rect)

            text_surface = self.font.render(str(i + 2), True, BLACK) 
            text_rect = text_surface.get_rect()
            text_rect.center = (x2, y2 - int(self.cell_size * 0.25))
            screen.blit(text_surface, text_rect)

        self.draw_knight(screen, last_pos)
        self.index += 1

    def draw_knight(self, screen, position):
        x, y = position
        x -= self.knight_image.get_width() // 2     
        y = y - (self.knight_image.get_height() // 2)  +  (self.cell_size * 0.15)
        screen.blit(self.knight_image, (x, y))
         
    def draw_cross(self, screen):
        x, y = self.position
        top_left_x =  self.start_x + (x * self.cell_size)
        top_left_y =  self.start_y + (y * self.cell_size)
        bottom_left_y = top_left_y + self.cell_size

        pygame.draw.line(screen, RED, (top_left_x, top_left_y), (top_left_x + self.cell_size, top_left_y + self.cell_size), 5)
        pygame.draw.line(screen, RED, (top_left_x, bottom_left_y), (top_left_x + self.cell_size, top_left_y), 5)

    def reset_squares(self):
        self.chosen_square = None
        self.highlighted_square = None
        self.index = 1

    def update(self, new_n):
        if new_n != self.n:
            self.__init__(new_n)
        current_position = self.position
        if not self.chosen_square and self.index == 1 or self.index >= self.n**2:
            if self.invalid_square != current_position:
                self.invalid_square = None
            self.highlighted_square = current_position

    def is_valid_position(self):
        col, row = self.position
        return (0 <= col < self.n) and (0 <= row < self.n)
          
    @property
    def position(self):
        x, y = pygame.mouse.get_pos()
        col = x // self.cell_size
        row = y // self.cell_size
        return (col, row)
    
class UI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pygame Game")
        self.clock = pygame.time.Clock()
        
        self.n_input_range = InputRange(850, 250, 300, 25, 5, 30, 8)
        self.FPS_input_range = InputRange(850, 500, 300, 25, 1, 60, 30)
        self.grid = Grid(self.n_input_range.value)

        self.font = pygame.font.Font(None, int(50))

        self.title = self.font.render("The Knight's Tour", True, BLACK)
        self.title_rect = self.title.get_rect(center=(995, 100))



        self.texts = [
            ["Board Size", [995, 220]],
            ["FPS", [995, 470]],
            [self.n_input_range.value, [995, 300]],
            [self.FPS_input_range.value, [995, 550]]
        ]
        
    def handle_events(self):
        for event in pygame.event.get():
            self.FPS_input_range.update(event)
            self.n_input_range.update(event)

            if event.type == pygame.QUIT:
                return False
    
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                if self.grid.is_valid_position():  
                    if self.grid.index >= self.n_input_range.value ** 2:
                        self.grid.reset_squares()

                    if not self.grid.chosen_square:
                        path = self.knights_tour(self.grid.position, self.n_input_range.value)
                        if not path:
                            self.grid.reset_squares()
                            self.grid.path = [] 
                            self.grid.invalid_square = self.grid.position
                        else:
                            self.grid.path = path
                            self.grid.chosen_square = self.grid.position
                            self.grid.invalid_square = None       
        return True

    def update(self):
        self.grid.update(self.n_input_range.value)

        self.texts[2][0] = self.n_input_range.value
        self.texts[3][0] = self.FPS_input_range.value

    
    def draw(self):
        self.screen.fill(WHITE)
        self.grid.draw(self.screen)
        
        if self.grid.path:
            self.grid.draw_path(self.screen)
        
        if self.grid.invalid_square:
            self.grid.draw_cross(self.screen)

        self.FPS_input_range.draw(self.screen)
        self.n_input_range.draw(self.screen)

        self.screen.blit(self.title, self.title_rect)

        for text, rect_center in self.texts:
            text_surface = self.font.render(str(text), True, BLACK)
            self.screen.blit(text_surface, text_surface.get_rect(center=rect_center))


        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS_input_range.value)
        pygame.quit()
        sys.exit()

    def knights_tour(self, start, n):

        def is_valid_move(x, y, board):
            return 0 <= x < n and 0 <= y < n and board[x][y] == -1

        def get_next_moves(x, y, board):
            return [(x + x2, y + y2) for (x2, y2) in zip(dx, dy) if is_valid_move(x + x2, y + y2, board)]

        def knights_tour_util(x, y, move_number, board, path):
            if move_number == n**2:
                path.append((x, y))
                return True

            # Generate Next Moves
            moves = get_next_moves(x, y, board)
            moves.sort(key=lambda pos: len(get_next_moves(*pos, board)))

            if not moves:
                # No valid moves from this position, trigger backtracking
                print(f"No valid moves from ({x}, {y})")
                return False
                

            for x_new, y_new in moves:
                # Make Move and Recursive Call
                board[x_new][y_new] = move_number
                path.append((x_new, y_new))
                
                if knights_tour_util(x_new, y_new, move_number+1, board, path):
                    return True
                else:
                    return False
            
                #board[x_new][y_new] = -1
                #path.pop()

            return False
        
        self.start_x, self.start_y = start

        # Initialize the chessboard
        board = [[-1 for _ in range(n)] for _ in range(n)]
        path = [(self.start_x, self.start_y)]

        # Possible moves for a knight
        dx = [-2, -1, 1, 2, 2, 1, -1, -2]
        dy = [-1, -2, -2, -1, 1, 2, 2, 1]

        # Set the starting position
        
        board[self.start_x][self.start_y] = 0

        # Find the knight's tour
        if knights_tour_util(self.start_x, self.start_y, 1, board, path):
            return path[:-1] 
        else:
            return False

class InputRange:
    def __init__(self, x, y, width, height, min_value, max_value, initial_value):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.visual_range = max_value - min_value
        self.value = initial_value
        self.is_dragging = False

        self.slider_color = (100, 100, 100)
        self.slider_button_radius = 10
        self.slider_button_color = (200, 50, 50)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.x - self.slider_button_radius <= mouse_x <= self.x + self.width + self.slider_button_radius \
                        and self.y <= mouse_y <= self.y + self.height:
                    self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        if self.is_dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            self.value = ((mouse_x - self.x) / self.width) * self.visual_range + self.min_value
            self.value = int(max(self.min_value, min(self.value, self.max_value)))

    def draw(self, screen):
        pygame.draw.rect(screen, self.slider_color, (self.x, self.y, self.width, self.height))
        slider_button_x = self.x + ((self.value - self.min_value) / self.visual_range) * self.width
        pygame.draw.circle(screen, self.slider_button_color,
                           (int(slider_button_x), self.y + self.height // 2),
                           self.slider_button_radius)
        
simulation = UI()
simulation.run()

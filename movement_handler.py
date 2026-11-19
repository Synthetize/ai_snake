from enums import Direction
from collections import deque

# Offset vettoriali (delta_row, delta_col) per ogni direzione
DIRECTIONS_OFFSET = {
    Direction.UP:    (-1,  0),  # row - 1, col + 0
    Direction.DOWN:  ( 1,  0),  # row + 1, col + 0
    Direction.LEFT:  ( 0, -1),  # row + 0, col - 1
    Direction.RIGHT: ( 0,  1),  # row + 0, col + 1
}


_NEIGHBOR_OFFSETS = ((-1, 0), (1, 0), (0, -1), (0, 1))


class MovementHandler:
    """
    Gestisce i calcoli cinematici del movimento su griglia discreta.
    """

    def __init__(self):
        self._neighbors_cache = {}

    def get_next_position(self, direction: Direction, snake_head_position: tuple[int, int]) -> tuple[int, int]:
        """
        Data una direzione e la posizione attuale della testa (row, col),
        restituisce la nuova coordinata (row, col) risultante.
        """
        head_row, head_col = snake_head_position
        delta_row, delta_col = DIRECTIONS_OFFSET[direction]
        return (head_row + delta_row, head_col + delta_col)


    def _neighbors(self, rows: int, cols: int) -> list[tuple[int, ...]]:
        """
        Lista di adiacenza precalcolata (e messa in cache) per la griglia rows x cols:
        la cella (r, c) è l'indice piatto r * cols + c. Nessun controllo dei bordi nella BFS.
        """
        cached = self._neighbors_cache.get((rows, cols))
        if cached is None:
            cached = []
            for r in range(rows):
                for c in range(cols):
                    around = []
                    for dr, dc in _NEIGHBOR_OFFSETS:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            around.append(nr * cols + nc)
                    cached.append(tuple(around))
            self._neighbors_cache[(rows, cols)] = cached
        return cached

    @staticmethod
    def build_release_times(snake_body, rows: int, cols: int) -> list[int]:
        """
        Lista piatta (indice r * cols + c) con, per ogni cella occupata dal serpente, dopo
        quante mosse si libera; 0 per le celle già libere.
        snake_body[0] è la testa, snake_body[-1] la coda: la coda si libera dopo 1 mossa,
        il segmento di indice i dopo (L - i) mosse.
        """
        release = [0] * (rows * cols)
        length = len(snake_body)
        for i, (r, c) in enumerate(snake_body):
            release[r * cols + c] = length - i
        return release

    def count_reachable_space(self, start_pos: tuple[int, int], rows: int, cols: int, release_times: list[int]) -> int:
        """
        Flood-fill DINAMICO: conta le celle raggiungibili entrando in `start_pos` con la
        prossima mossa, tenendo conto che il corpo si ritrae mentre il serpente si muove.

        Una cella raggiunta alla mossa `d` (start_pos = mossa 1) è percorribile se è vuota
        (release 0) oppure se il segmento che la occupa si è già liberato (d > release).
        Una cella bloccata non viene marcata come visitata: può essere raggiunta più tardi
        da un altro vicino, quando nel frattempo la coda si è spostata.
        Nessun limite di ricerca: la griglia è piccola e il cap saturava la feature.

        BFS per livelli (niente tupla (r, c, d) in coda): `d` è il numero del livello.
        """
        start_row, start_col = start_pos
        if not (0 <= start_row < rows and 0 <= start_col < cols):
            return 0
        start = start_row * cols + start_col
        if release_times[start] > 0:  # alla mossa 1 nessun segmento si è ancora liberato
            return 0

        neighbors = self._neighbors(rows, cols)
        visited = bytearray(rows * cols)
        visited[start] = 1
        frontier = [start]
        count = 0
        depth = 1

        while frontier:
            count += len(frontier)
            depth += 1
            next_frontier = []
            for cell in frontier:
                for n in neighbors[cell]:
                    if not visited[n] and release_times[n] < depth:
                        visited[n] = 1
                        next_frontier.append(n)
            frontier = next_frontier

        return count

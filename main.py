import tkinter as tk
from tkinter import messagebox
import copy, random

# ---------- Game constants ----------
HUMAN = "X"
AI = "O"
EMPTY = ""
WIN_LINES = [
    (0,1,2), (3,4,5), (6,7,8),    # rows
    (0,3,6), (1,4,7), (2,5,8),    # cols
    (0,4,8), (2,4,6)              # diagonals
]

# ---------- Minimax AI ----------
class MinimaxAI:
    def __init__(self):
        self.nodes_evaluated = 0

    def reset_counter(self):
        self.nodes_evaluated = 0

    def evaluate(self, board):
        for a,b,c in WIN_LINES:
            if board[a] == board[b] == board[c] and board[a] != EMPTY:
                return 1 if board[a] == AI else -1
        return 0

    def minimax(self, board, alpha, beta, maximizing):
        self.nodes_evaluated += 1
        score = self.evaluate(board)
        if score != 0:
            return score, None
        if all(cell != EMPTY for cell in board):
            return 0, None

        best_move = None
        if maximizing:
            max_eval = -999
            for i in range(9):
                if board[i] == EMPTY:
                    board[i] = AI
                    eval_score, _ = self.minimax(board, alpha, beta, False)
                    board[i] = EMPTY
                    if eval_score > max_eval:
                        max_eval, best_move = eval_score, i
                    alpha = max(alpha, eval_score)
                    if beta <= alpha: break
            return max_eval, best_move
        else:
            min_eval = 999
            for i in range(9):
                if board[i] == EMPTY:
                    board[i] = HUMAN
                    eval_score, _ = self.minimax(board, alpha, beta, True)
                    board[i] = EMPTY
                    if eval_score < min_eval:
                        min_eval, best_move = eval_score, i
                    beta = min(beta, eval_score)
                    if beta <= alpha: break
            return min_eval, best_move

    def best_move(self, board):
        self.reset_counter()
        _, move = self.minimax(board, -999, 999, True)
        return move, self.nodes_evaluated


class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Tic Tac Toe — Smart AI")
        self.root.configure(bg="#1a1a2e")

        self.ai = MinimaxAI()
        self.board = [EMPTY]*9
        self.buttons = []
        self.human_turn = True
        self.game_over = False

        # --- Title ---
        title = tk.Label(
            root, text="Tic Tac Toe", font=("Poppins", 24, "bold"),
            bg="#1a1a2e", fg="#00ADB5"
        )
        title.pack(pady=(10,0))

        # --- Status Frame ---
        self.status_var = tk.StringVar(value="Your turn (X)")
        status_label = tk.Label(
            root, textvariable=self.status_var, font=("Poppins", 12),
            bg="#1a1a2e", fg="#EEEEEE"
        )
        status_label.pack(pady=(5,0))

        # --- Node Count ---
        self.nodes_var = tk.StringVar(value="AI nodes evaluated: 0")
        node_label = tk.Label(
            root, textvariable=self.nodes_var, font=("Poppins", 10),
            bg="#1a1a2e", fg="#7DE2D1"
        )
        node_label.pack(pady=(0,8))

        # --- Board Frame ---
        board_frame = tk.Frame(root, bg="#16213E", bd=0)
        board_frame.pack(padx=10, pady=10)

        for i in range(9):
            btn = tk.Button(
                board_frame, text="", font=("Poppins", 20, "bold"), width=5, height=2,
                bg="#0F3460", fg="#EEEEEE", activebackground="#533483",
                activeforeground="#F8F9D7", relief="flat",
                command=lambda i=i: self.player_move(i)
            )
            btn.grid(row=i//3, column=i%3, padx=6, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#533483"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#0F3460"))
            self.buttons.append(btn)

        # --- Control Buttons ---
        control_frame = tk.Frame(root, bg="#1a1a2e")
        control_frame.pack(pady=(5,10))

        restart = tk.Button(
            control_frame, text="Restart", command=self.restart,
            bg="#00ADB5", fg="#EEEEEE", font=("Poppins", 11, "bold"),
            relief="flat", padx=12, pady=4, width=10
        )
        restart.grid(row=0, column=0, padx=10)

        quit_btn = tk.Button(
            control_frame, text="Quit", command=root.quit,
            bg="#FF5722", fg="white", font=("Poppins", 11, "bold"),
            relief="flat", padx=12, pady=4, width=10
        )
        quit_btn.grid(row=0, column=1, padx=10)

    # Game logic
    def player_move(self, index):
        if self.game_over or not self.human_turn or self.board[index] != EMPTY:
            return
        self.board[index] = HUMAN
        self.update_ui()
        if self.check_end(): return
        self.human_turn = False
        self.status_var.set("AI thinking...")
        self.root.after(300, self.ai_move)

    def ai_move(self):
        move, nodes = self.ai.best_move(copy.copy(self.board))
        if move is None:
            move = random.choice([i for i,v in enumerate(self.board) if v == EMPTY])
        self.board[move] = AI
        self.nodes_var.set(f"AI nodes evaluated: {nodes}")
        print(f"[AI] nodes evaluated: {nodes}")
        self.update_ui()
        if self.check_end(): return
        self.human_turn = True
        self.status_var.set("Your turn (X)")

    def check_end(self):
        winner = None
        for a,b,c in WIN_LINES:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] != EMPTY:
                winner = self.board[a]
                self.highlight_win((a,b,c))
                break
        if winner:
            self.game_over = True
            msg = "You win! 🎉" if winner == HUMAN else "AI wins! 🤖"
            self.status_var.set(msg)
            self.root.after(500, lambda: messagebox.showinfo("Game Over", msg))
            return True
        if all(v != EMPTY for v in self.board):
            self.game_over = True
            self.status_var.set("Draw 🤝")
            self.root.after(500, lambda: messagebox.showinfo("Game Over", "It's a Draw!"))
            return True
        return False

    def highlight_win(self, triple):
        colors = ["#F9ED69", "#F08A5D", "#B83B5E"]
        for step in range(6):
            color = colors[step % len(colors)]
            self.root.after(step*150, lambda c=color: [
                self.buttons[i].config(bg=c) for i in triple
            ])

    def update_ui(self):
        for i, btn in enumerate(self.buttons):
            value = self.board[i]
            btn.config(text=value)
            if value == HUMAN:
                btn.config(fg="#00EAD3")
            elif value == AI:
                btn.config(fg="#FF449F")
            else:
                btn.config(fg="#EEEEEE", bg="#0F3460")

    def restart(self):
        self.board = [EMPTY]*9
        self.game_over = False
        self.human_turn = True
        self.status_var.set("Your turn (X)")
        self.nodes_var.set("AI nodes evaluated: 0")
        for b in self.buttons:
            b.config(text="", bg="#0F3460", fg="#EEEEEE")


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = TicTacToeGUI(root)
    root.mainloop()
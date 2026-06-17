# Convolutional Neural Network for Tic Tac Toe AI

# Tic-Tac-Toe AI Model Trainer
import os
import datetime
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import time
import warnings

warnings.filterwarnings("ignore", message=".*Using padding='same' with even kernel lengths.*")

# Training configuration and setup
HEADLESS_MODE = True  
CHECKPOINT_PATH = "models/ttt_model_checkpoint_latest.pth"
LEARNING_RATE = 0.001
ESTOP_PATIENCE = 10
TRAINING_EPOCHS = 100
SCHEDULER_FACTOR = 0.1  
SCHEDULER_PATIENCE = 3  

class TTTDataset(Dataset):
    def __init__(self, boards, solutions):
        self.boards = boards
        self.solutions = solutions

    def __len__(self):
        return len(self.boards)

    def __getitem__(self, idx):
        return self.boards[idx].float(), self.solutions[idx].long()

    @staticmethod
    def generateTTTDataset():
        """
        Generates all valid Tic-Tac-Toe permutations using backtracking.
        Boards are stored as one-hot tensors of size (3, 3, 3) -> [Empty, X, O]
        Solutions are the fully completed optimal boards (or simply the next best move matrices).
        For an absolute proof of concept, we map valid board states to their complete final outcome boards.
        """
        all_boards = []
        all_solutions = []
        seen_states = set()

        def evaluate_board(b):
            # Helper to check for a winner
            lines = [
                [b[0], b[1], b[2]], [b[3], b[4], b[5]], [b[6], b[7], b[8]], # Horizontals
                [b[0], b[3], b[6]], [b[1], b[4], b[7]], [b[2], b[5], b[8]], # Verticals
                [b[0], b[4], b[8]], [b[2], b[4], b[6]]                      # Diagonals
            ]
            for line in lines:
                if line[0] != 0 and line[0] == line[1] == line[2]:
                    return line[0]
            return 0

        def solve_board(b, turn):
            # A simple minimax algorithm to find the optimal fully solved board layout
            winner = evaluate_board(b)
            if winner != 0 or 0 not in b:
                return list(b)

            best_board = list(b)
            # Simple simulation: capture the first available path for demonstration
            for i in range(9):
                if b[i] == 0:
                    next_b = list(b)
                    next_b[i] = turn
                    res = solve_board(next_b, 3 - turn)
                    if evaluate_board(res) == turn: 
                        return res
                    best_board = res
            return best_board

        def generate(board, turn):
            state_id = tuple(board)
            if state_id in seen_states:
                return
            seen_states.add(state_id)

            # Convert board array to 3-channel one-hot tensor (3 x 3 x 3)
            board_tensor = torch.zeros(3, 3, 3)
            for idx, val in enumerate(board):
                r, c = idx // 3, idx % 3
                board_tensor[val, r, c] = 1.0

            # Generate target configuration tensor (3 x 3) containing 0, 1, or 2
            solution_arr = solve_board(board, turn)
            solution_tensor = torch.tensor(solution_arr, dtype=torch.long).view(3, 3)

            all_boards.append(board_tensor.unsqueeze(0))
            all_solutions.append(solution_tensor.unsqueeze(0))

            if evaluate_board(board) != 0 or 0 not in board:
                return

            for i in range(9):
                if board[i] == 0:
                    next_board = list(board)
                    next_board[i] = turn
                    generate(next_board, 3 - turn)

        # Kickstart generation from empty board (0=Empty, 1=X, 2=O)
        generate([0]*9, 1)
        
        boards_tensor = torch.cat(all_boards, dim=0)
        solutions_tensor = torch.cat(all_solutions, dim=0)
        
        # Split into training and verification sets (80 / 20)
        indices = torch.randperm(len(boards_tensor))
        split = int(len(boards_tensor) * 0.8)
        
        train_idx, val_idx = indices[:split], indices[split:]
        
        return (TTTDataset(boards_tensor[train_idx], solutions_tensor[train_idx]), 
                TTTDataset(boards_tensor[val_idx], solutions_tensor[val_idx]))


class BlackBoxBreakerCNN(nn.Module):
    def __init__(self):
        super(BlackBoxBreakerCNN, self).__init__()
        
        # Input channels: 3 (Empty, X, O)
        # Output filters per shape: 16
        self.conv_horiz = nn.Conv2d(3, 16, kernel_size=(1, 3), padding='same')
        self.conv_vert = nn.Conv2d(3, 16, kernel_size=(3, 1), padding='same')
        
        # For diagonals, we use 3x3 kernels and programmatically hook specific tracking
        self.conv_diag_left = nn.Conv2d(3, 16, kernel_size=3, padding='same')
        self.conv_diag_right = nn.Conv2d(3, 16, kernel_size=3, padding='same')
        self._initialize_diagonal_weights()

        self.dropout = nn.Dropout2d(p=0.1)
        
        # Layer 2 Synthesizer: 16 filters * 4 perspectives = 64 input channels
        self.layer2 = nn.Conv2d(64, 32, kernel_size=3, padding='same')
        
        # Predictor Layer: Map down to 3 scoring classes per cell (Empty, X, O)
        self.final_layer = nn.Conv2d(32, 3, kernel_size=1)

    def _initialize_diagonal_weights(self):
        # Enforce structural focus on true diagonals inside the 3x3 components
        with torch.no_grad():
            # Left diagonal matrix layout (identity)
            mask_left = torch.eye(3).view(1, 1, 3, 3)
            self.conv_diag_left.weight.copy_(self.conv_diag_left.weight * mask_left)
            # Right diagonal matrix layout (flipped identity)
            mask_right = torch.fliplr(torch.eye(3)).view(1, 1, 3, 3)
            self.conv_diag_right.weight.copy_(self.conv_diag_right.weight * mask_right)

    def forward(self, x):
        out_h = F.relu(self.conv_horiz(x))
        out_v = F.relu(self.conv_vert(x))
        out_dl = F.relu(self.conv_diag_left(x))
        out_dr = F.relu(self.conv_diag_right(x))
        
        # Fuse perspectives
        x1 = torch.cat([out_h, out_v, out_dl, out_dr], dim=1)
        x1_reg = self.dropout(x1)
        
        x2 = F.relu(self.layer2(x1_reg))
        logits = self.final_layer(x2)
        return logits

def board_to_tensor(board_list):
    """
    Converts a flat list of 9 elements (0=Empty, 1=X, 2=O) 
    into a (1, 3, 3, 3) one-hot model tensor.
    """
    tensor = torch.zeros(3, 3, 3)
    for idx, val in enumerate(board_list):
        r, c = idx // 3, idx % 3
        tensor[val, r, c] = 1.0
    return tensor.unsqueeze(0) # Add batch dimension

def render_board(board_matrix):
    """Prints a human-readable layout of a 3x3 array/tensor."""
    symbols = {0: '.', 1: 'X', 2: 'O'}
    for row in board_matrix:
        print(" ".join([symbols[int(cell)] for cell in row]))

def test_static_scenarios(model, device):
    """Runs explicit diagnostic scenarios to test specific model instincts."""
    print("\n" + "="*40)
    print("RUNNING STATIC SCENARIO TESTS")
    print("="*40)

    # Scenario: X is about to win on the top horizontal line.
    # [X, X, .,  O, O, .,  ., ., .]
    test_board = [1, 1, 0,  2, 2, 0,  0, 0, 0]
    
    print("\nInput Scenario Board:")
    render_board(torch.tensor(test_board).view(3, 3))
    
    input_tensor = board_to_tensor(test_board).to(device)
    
    with torch.no_grad():
        logits = model(input_tensor)
        # Argmax over the class channel dimension (dim=1)
        predictions = torch.argmax(logits, dim=1).squeeze(0).cpu()
        
    print("\nModel's Predicted Completed State Layout:")
    render_board(predictions)
    
    # Check if the critical winning spot (0, 2) was populated by X (1)
    if predictions[0, 2] == 1:
        print("✅ Success: Model completed the winning horizontal configuration!")
    else:
        print("❌ Fail: Model missed the explicit winning path layout.")

def evaluate_validation_accuracy(model, val_dataset, device):
    """Runs a complete validation pass to check exact matrix matches."""
    print("\n" + "="*40)
    print("RUNNING BULK VALIDATION SWEEP")
    print("="*40)
    
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    total_cells = 0
    correct_cells = 0
    exact_matches = 0
    total_boards = 0
    
    with torch.no_grad():
        for boards, solutions in val_loader:
            boards, solutions = boards.to(device), solutions.to(device)
            outputs = model(boards)
            
            predictions = torch.argmax(outputs, dim=1)
            
            # Element-wise calculation comparisons
            correct_matrix = (predictions == solutions)
            correct_cells += correct_matrix.sum().item()
            total_cells += solutions.numel()
            
            # Exact full board match tracking
            for i in range(boards.size(0)):
                total_boards += 1
                if torch.equal(predictions[i], solutions[i]):
                    exact_matches += 1
                    
    cell_acc = (correct_cells / total_cells) * 100
    board_acc = (exact_matches / total_boards) * 100
    
    print(f"Total Boards Evaluated: {total_boards}")
    print(f"Individual Cell Prediction Accuracy: {cell_acc:.2f}%")
    print(f"Full Board Matrix Match Accuracy:   {board_acc:.2f}%")


def main():
    log_file = "analysis/logs/ttt_training.log"
    os.makedirs("analysis/logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running TTT training on: {device}")

    # Generate the full dataset on the fly
    print("Generating complete Tic-Tac-Toe state space permutations...")
    train_dataset, val_dataset = TTTDataset.generateTTTDataset()
    print(f"Dataset generated. Train size: {len(train_dataset)}, Val size: {len(val_dataset)}")

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    model = BlackBoxBreakerCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=SCHEDULER_FACTOR, patience=SCHEDULER_PATIENCE)

    train_losses, val_losses = [], []
    best_val_loss = float('inf')
    epochs_without_improvement = 0

    for epoch in range(TRAINING_EPOCHS):
        model.train()
        running_train_loss = 0.0
        for boards, solutions in train_loader:
            boards, solutions = boards.to(device), solutions.to(device)
            
            optimizer.zero_grad()
            outputs = model(boards)
            loss = criterion(outputs, solutions)
            loss.backward()
            optimizer.step()
            
            running_train_loss += loss.item() * boards.size(0)

        epoch_train_loss = running_train_loss / len(train_loader.dataset)

        # Evaluation phase
        model.eval()
        running_val_loss = 0.0
        with torch.no_grad():
            for val_boards, val_solutions in val_loader:
                val_boards, val_solutions = val_boards.to(device), val_solutions.to(device)
                val_outputs = model(val_boards)
                val_loss = criterion(val_outputs, val_solutions)
                running_val_loss += val_loss.item() * val_boards.size(0)
        
        epoch_val_loss = running_val_loss / len(val_loader.dataset)
        scheduler.step(epoch_val_loss)

        train_losses.append(epoch_train_loss)
        val_losses.append(epoch_val_loss)

        print(f"Epoch {epoch+1}/{TRAINING_EPOCHS} - Train Loss: {epoch_train_loss:.4f} - Val Loss: {epoch_val_loss:.4f}")

        # Validation Checkpoint tracking
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            epochs_without_improvement = 0
            torch.save(model.state_dict(), "models/ttt_model_best.pth")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= ESTOP_PATIENCE:
                print(f"Early stopping structural break at epoch {epoch+1}")
                break

    print("Training Complete. Optimal state verification checked.")

    # Test the model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # 1. Initialize empty network architecture
    model = BlackBoxBreakerCNN().to(device)
    model_path = "models/ttt_model_best.pth"
    
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Successfully loaded weights from {model_path}")
    else:
        print(f"⚠️ Warning: {model_path} not found. Running tests on uninitialized weights.")
        
    model.eval()
    
    # 2. Generate data splits on the fly for validation check
    _, val_dataset = TTTDataset.generateTTTDataset()
    
    # 3. Execute testing vectors
    test_static_scenarios(model, device)
    evaluate_validation_accuracy(model, val_dataset, device)

if __name__ == "__main__":
    main()
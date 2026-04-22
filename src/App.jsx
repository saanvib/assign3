import * as React from 'react'

function Square({ value, onSquareClick, isSelected }) {
  return (
    <button
      className={'square' + (isSelected ? ' selected' : '')}
      onClick={onSquareClick}
    >
      {value}
    </button>
  );
}

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6],
  ];
  for (const [a, b, c] of lines) {
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}

function isAdjacent(from, to) {
  const fromRow = Math.floor(from / 3);
  const fromCol = from % 3;
  const toRow = Math.floor(to / 3);
  const toCol = to % 3;
  return (
    Math.abs(fromRow - toRow) <= 1 &&
    Math.abs(fromCol - toCol) <= 1 &&
    from !== to
  );
}

export default function App() {
  const [squares, setSquares] = React.useState(Array(9).fill(null));
  const [isXNext, setIsXNext] = React.useState(true);
  const [selectedSquare, setSelectedSquare] = React.useState(null);

  const xCount = squares.filter(s => s === 'X').length;
  const oCount = squares.filter(s => s === 'O').length;
  const currentPlayer = isXNext ? 'X' : 'O';
  const currentPlayerCount = isXNext ? xCount : oCount;
  const isMovingPhase = currentPlayerCount >= 3;

  const winner = calculateWinner(squares);

  function handleClick(i) {
    if (winner) return;

    if (!isMovingPhase) {
      if (squares[i]) return;
      const nextSquares = squares.slice();
      nextSquares[i] = currentPlayer;
      setSquares(nextSquares);
      setIsXNext(!isXNext);
      return;
    }

    // Moving phase: two-click interaction
    if (selectedSquare === null) {
      if (squares[i] === currentPlayer) {
        setSelectedSquare(i);
      }
      return;
    }

    // Destination must be empty and adjacent, otherwise revert
    if (squares[i] !== null || !isAdjacent(selectedSquare, i)) {
      setSelectedSquare(null);
      return;
    }

    // Build the resulting board to check win and center constraint
    const nextSquares = squares.slice();
    nextSquares[i] = currentPlayer;
    nextSquares[selectedSquare] = null;

    // Center constraint: if current player occupies center, move must win or vacate center
    if (squares[4] === currentPlayer) {
      const wouldWin = calculateWinner(nextSquares) === currentPlayer;
      const vacatesCenter = selectedSquare === 4;
      if (!wouldWin && !vacatesCenter) {
        setSelectedSquare(null);
        return;
      }
    }

    setSquares(nextSquares);
    setSelectedSquare(null);
    setIsXNext(!isXNext);
  }

  let status;
  if (winner) {
    status = 'Winner: ' + winner;
  } else {
    status = 'Next player: ' + currentPlayer;
  }

  return (
    <div className="game">
      <div className="game-board">
        <div className="status">{status}</div>
        <div className="board-row">
          <Square value={squares[0]} onSquareClick={() => handleClick(0)} isSelected={selectedSquare === 0} />
          <Square value={squares[1]} onSquareClick={() => handleClick(1)} isSelected={selectedSquare === 1} />
          <Square value={squares[2]} onSquareClick={() => handleClick(2)} isSelected={selectedSquare === 2} />
        </div>
        <div className="board-row">
          <Square value={squares[3]} onSquareClick={() => handleClick(3)} isSelected={selectedSquare === 3} />
          <Square value={squares[4]} onSquareClick={() => handleClick(4)} isSelected={selectedSquare === 4} />
          <Square value={squares[5]} onSquareClick={() => handleClick(5)} isSelected={selectedSquare === 5} />
        </div>
        <div className="board-row">
          <Square value={squares[6]} onSquareClick={() => handleClick(6)} isSelected={selectedSquare === 6} />
          <Square value={squares[7]} onSquareClick={() => handleClick(7)} isSelected={selectedSquare === 7} />
          <Square value={squares[8]} onSquareClick={() => handleClick(8)} isSelected={selectedSquare === 8} />
        </div>
      </div>
    </div>
  );
}

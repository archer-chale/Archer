import AppRouter from './routes';

function App() {
  return (
    <div style={{ 
      width: '100%',
      minHeight: '100vh',
      backgroundColor: '#f8f9fa',
      overflow: 'hidden'
    }}>
      <AppRouter />
    </div>
  );
}

export default App;
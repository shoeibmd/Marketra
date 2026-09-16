import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught Error in Component Tree:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6 font-mono">
          <div className="border border-red-800 bg-slate-900 rounded-lg p-6 max-w-md w-full shadow-2xl">
            <h2 className="text-red-400 font-bold text-lg mb-2">Terminal Shell Error</h2>
            <p className="text-slate-400 text-xs mb-4">
              {this.state.error?.message || 'An unexpected rendering error occurred inside the panel shell.'}
            </p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="bg-red-900 hover:bg-red-800 text-white text-xs px-4 py-2 rounded transition-colors"
            >
              Reset Application State
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

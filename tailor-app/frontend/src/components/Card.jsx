export function Card({ children, className }) {
    return (
      <div className={`border border-gray-500 rounded-lg p-4 shadow-lg ${className}`}>
        {children}
      </div>
    );
  }
  
  export function CardContent({ children, className }) {
    return <div className={`p-2 ${className}`}>{children}</div>;
  }
  
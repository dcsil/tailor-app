import React from 'react';
import ReactMarkdown from 'react-markdown';
import '../markdown.css'

const FormattedAnalysis = ({ analysis }) => {
  return (
    <div className="markdown-body">
      {<ReactMarkdown>{analysis}</ReactMarkdown>}
    </div>
  );
};

export default FormattedAnalysis;

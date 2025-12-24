import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { codeAPI } from "../services/api";
import "./FeedbackPage.css";

/**
 * FeedbackPage - Full page for displaying AI feedback on submissions
 */
const FeedbackPage = () => {
  const { submissionId } = useParams();
  const navigate = useNavigate();
  
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submissionData, setSubmissionData] = useState(null);

  useEffect(() => {
    const fetchFeedback = async () => {
      const maxAttempts = 15;
      const pollInterval = 2000;

      for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
          const response = await codeAPI.getAIFeedback(submissionId);
          const data = response.data;

          if (data.has_feedback) {
            setFeedback({
              text: data.feedback,
              verdictType: data.verdict_type,
              modelUsed: data.model_used,
              generatedAt: data.generated_at,
            });
            setSubmissionData(data);
            setLoading(false);
            return;
          }

          if (data.status === 'error') {
            setError(data.error || 'Failed to generate feedback');
            setLoading(false);
            return;
          }

          // Still generating - wait and retry
          await new Promise(resolve => setTimeout(resolve, pollInterval));
        } catch (err) {
          console.error('Error fetching AI feedback:', err);
          if (attempt === maxAttempts - 1) {
            setError('Unable to load AI feedback. Please try again later.');
            setLoading(false);
          }
        }
      }

      if (loading) {
        setError('AI feedback is taking longer than expected. Please check back later.');
        setLoading(false);
      }
    };

    fetchFeedback();
  }, [submissionId]);

  const handleBackToDashboard = () => {
    navigate('/student/dashboard');
  };

  const getVerdictInfo = (verdictType) => {
    switch (verdictType) {
      case 'accepted':
        return { icon: '✅', label: 'Passed', color: '#22c55e' };
      case 'wrong_answer':
        return { icon: '❌', label: 'Failed', color: '#ef4444' };
      case 'error':
        return { icon: '⚠️', label: 'Error', color: '#f59e0b' };
      default:
        return { icon: '📝', label: 'Review', color: '#6366f1' };
    }
  };

  const formatFeedback = (text) => {
    if (!text) return null;
    
    // Convert markdown-style headers and formatting to JSX
    const lines = text.split('\n');
    const elements = [];
    let currentParagraph = [];

    lines.forEach((line, index) => {
      // Handle headers with emojis
      if (line.startsWith('## ')) {
        if (currentParagraph.length > 0) {
          elements.push(
            <p key={`p-${index}`} className="feedback-paragraph">
              {currentParagraph.join('\n')}
            </p>
          );
          currentParagraph = [];
        }
        elements.push(
          <h3 key={`h-${index}`} className="feedback-section-header">
            {line.replace('## ', '')}
          </h3>
        );
      } else if (line.startsWith('# ')) {
        if (currentParagraph.length > 0) {
          elements.push(
            <p key={`p-${index}`} className="feedback-paragraph">
              {currentParagraph.join('\n')}
            </p>
          );
          currentParagraph = [];
        }
        elements.push(
          <h2 key={`h-${index}`} className="feedback-main-header">
            {line.replace('# ', '')}
          </h2>
        );
      } else if (line.startsWith('- ') || line.startsWith('* ')) {
        if (currentParagraph.length > 0) {
          elements.push(
            <p key={`p-${index}`} className="feedback-paragraph">
              {currentParagraph.join('\n')}
            </p>
          );
          currentParagraph = [];
        }
        elements.push(
          <li key={`li-${index}`} className="feedback-list-item">
            {line.replace(/^[-*] /, '')}
          </li>
        );
      } else if (line.trim() === '') {
        if (currentParagraph.length > 0) {
          elements.push(
            <p key={`p-${index}`} className="feedback-paragraph">
              {currentParagraph.join('\n')}
            </p>
          );
          currentParagraph = [];
        }
      } else {
        currentParagraph.push(line);
      }
    });

    // Don't forget remaining paragraph
    if (currentParagraph.length > 0) {
      elements.push(
        <p key="p-last" className="feedback-paragraph">
          {currentParagraph.join('\n')}
        </p>
      );
    }

    return elements;
  };

  const verdictInfo = feedback ? getVerdictInfo(feedback.verdictType) : null;

  return (
    <div className="feedback-page">
      <div className="feedback-container">
        {/* Header */}
        <header className="feedback-header">
          <button className="back-button" onClick={handleBackToDashboard}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
          
          <div className="header-title">
            <div className="ai-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2a3 3 0 0 0-3 3v1a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                <path d="M19 10a7 7 0 0 1-14 0" />
                <path d="M12 17v5" />
                <path d="M8 22h8" />
              </svg>
            </div>
            <h1>AI Tutor Feedback</h1>
          </div>

          {verdictInfo && (
            <div 
              className="verdict-badge"
              style={{ backgroundColor: `${verdictInfo.color}20`, borderColor: verdictInfo.color }}
            >
              <span className="verdict-icon">{verdictInfo.icon}</span>
              <span style={{ color: verdictInfo.color }}>{verdictInfo.label}</span>
            </div>
          )}
        </header>

        {/* Main Content */}
        <main className="feedback-main">
          {loading && (
            <div className="loading-state">
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
              <h2>Generating AI Feedback...</h2>
              <p>Our AI tutor is analyzing your code submission. This may take a moment.</p>
              <div className="loading-tips">
                <p>💡 Tip: AI feedback helps you learn from both successes and mistakes!</p>
              </div>
            </div>
          )}

          {error && (
            <div className="error-state">
              <div className="error-icon">⚠️</div>
              <h2>Unable to Load Feedback</h2>
              <p>{error}</p>
              <button className="retry-button" onClick={() => window.location.reload()}>
                Try Again
              </button>
            </div>
          )}

          {feedback && !loading && (
            <div className="feedback-content">
              <div className="feedback-intro">
                {feedback.verdictType === 'accepted' && (
                  <p className="intro-text success">
                    🎉 Great job! Your solution passed all test cases. Here's a detailed review of your code.
                  </p>
                )}
                {feedback.verdictType === 'wrong_answer' && (
                  <p className="intro-text guidance">
                    💡 Your solution didn't pass all test cases. Let's understand what went wrong and how to improve.
                  </p>
                )}
                {feedback.verdictType === 'error' && (
                  <p className="intro-text error">
                    🔧 Your code encountered an error. Here's a detailed explanation to help you fix it.
                  </p>
                )}
              </div>

              <div className="feedback-body">
                {formatFeedback(feedback.text)}
              </div>

              <div className="feedback-footer">
                <p className="model-info">
                  Generated by {feedback.modelUsed || 'Gemini AI'}
                </p>
              </div>
            </div>
          )}
        </main>

        {/* Footer Actions */}
        <footer className="feedback-actions">
          <button className="action-button secondary" onClick={handleBackToDashboard}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 12h18M3 6h18M3 18h18" />
            </svg>
            View All Activities
          </button>
          <button className="action-button primary" onClick={handleBackToDashboard}>
            Continue Coding
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </footer>
      </div>
    </div>
  );
};

export default FeedbackPage;

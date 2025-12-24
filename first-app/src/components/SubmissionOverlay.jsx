import { useState, useEffect } from "react";
import { codeAPI } from "../services/api";
import "./SubmissionOverlay.css";

/**
 * SubmissionOverlay - Full screen overlay for submission process
 * 
 * States:
 * 1. Loading - Shows loading animation while grading
 * 2. Result - Shows Pass/Fail with Continue button
 * 3. AI Feedback - Shows AI-generated educational feedback
 */
const SubmissionOverlay = ({ 
  isVisible, 
  isLoading, 
  result, 
  submissionId,
  onClose 
}) => {
  const [stage, setStage] = useState('loading'); // 'loading' | 'result' | 'feedback'
  const [aiFeedback, setAiFeedback] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackError, setFeedbackError] = useState(null);

  // Reset state when overlay becomes visible
  useEffect(() => {
    if (isVisible) {
      if (isLoading) {
        setStage('loading');
      } else if (result) {
        setStage('result');
      }
      setAiFeedback(null);
      setFeedbackError(null);
    }
  }, [isVisible, isLoading, result]);

  // Update stage when loading completes
  useEffect(() => {
    if (!isLoading && result && stage === 'loading') {
      setStage('result');
    }
  }, [isLoading, result, stage]);

  // Fetch AI feedback when entering feedback stage
  const handleContinue = async () => {
    setStage('feedback');
    setFeedbackLoading(true);
    setFeedbackError(null);

    // Poll for AI feedback (it might still be generating)
    const maxAttempts = 10;
    const pollInterval = 2000; // 2 seconds

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await codeAPI.getAIFeedback(submissionId);
        const data = response.data;

        if (data.has_feedback) {
          setAiFeedback({
            feedback: data.feedback,
            verdictType: data.verdict_type,
          });
          setFeedbackLoading(false);
          return;
        }

        if (data.status === 'error') {
          setFeedbackError(data.error || 'Failed to generate feedback');
          setFeedbackLoading(false);
          return;
        }

        // Still generating - wait and retry
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (error) {
        console.error('Error fetching AI feedback:', error);
        if (attempt === maxAttempts - 1) {
          setFeedbackError('Unable to load AI feedback. Please try again later.');
          setFeedbackLoading(false);
        }
      }
    }

    // Timeout - feedback took too long
    if (feedbackLoading) {
      setFeedbackError('AI feedback is taking longer than expected. It will be available soon.');
      setFeedbackLoading(false);
    }
  };

  const handleClose = () => {
    setStage('loading');
    setAiFeedback(null);
    setFeedbackError(null);
    onClose();
  };

  if (!isVisible) return null;

  const isPassed = result?.success || result?.result === 'pass';

  return (
    <div className="submission-overlay">
      <div className="overlay-backdrop" />
      
      <div className="overlay-content">
        {/* Loading Stage */}
        {stage === 'loading' && (
          <div className="overlay-stage loading-stage">
            <div className="loading-spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
            </div>
            <h2>Evaluating Your Code</h2>
            <p>Running against all test cases...</p>
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        {/* Result Stage */}
        {stage === 'result' && result && (
          <div className="overlay-stage result-stage">
            <div className={`result-icon ${isPassed ? 'passed' : 'failed'}`}>
              {isPassed ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
              )}
            </div>
            
            <h2 className={isPassed ? 'text-passed' : 'text-failed'}>
              {isPassed ? 'All Tests Passed!' : 'Some Tests Failed'}
            </h2>
            
            <div className="result-stats">
              <div className="stat">
                <span className="stat-value">{result.score}%</span>
                <span className="stat-label">Score</span>
              </div>
              <div className="stat-divider" />
              <div className="stat">
                <span className="stat-value">{result.passed}/{result.total}</span>
                <span className="stat-label">Tests Passed</span>
              </div>
            </div>

            <button className="continue-btn" onClick={handleContinue}>
              Continue
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* AI Feedback Stage */}
        {stage === 'feedback' && (
          <div className="overlay-stage feedback-stage">
            <div className="feedback-header">
              <div className="feedback-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2a3 3 0 0 0-3 3v1a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                  <path d="M19 10a7 7 0 0 1-14 0" />
                  <path d="M12 17v5" />
                  <path d="M8 22h8" />
                </svg>
              </div>
              <h2>AI Tutor Feedback</h2>
              <p className="feedback-subtitle">
                {isPassed 
                  ? "Great job! Here are some suggestions to improve your code further."
                  : "Let's understand what went wrong and how to approach this differently."
                }
              </p>
            </div>

            <div className="feedback-body">
              {feedbackLoading && (
                <div className="feedback-loading">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <p>AI is analyzing your code...</p>
                </div>
              )}

              {feedbackError && (
                <div className="feedback-error">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <p>{feedbackError}</p>
                </div>
              )}

              {aiFeedback && (
                <div className="feedback-content">
                  <div className={`verdict-badge ${aiFeedback.verdictType}`}>
                    {aiFeedback.verdictType === 'accepted' && '✓ Code Review'}
                    {aiFeedback.verdictType === 'wrong_answer' && '💡 Guidance'}
                    {aiFeedback.verdictType === 'error' && '🔧 Error Help'}
                  </div>
                  <div className="feedback-text">
                    {aiFeedback.feedback}
                  </div>
                </div>
              )}
            </div>

            <button className="close-btn" onClick={handleClose}>
              Back to Editor
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmissionOverlay;

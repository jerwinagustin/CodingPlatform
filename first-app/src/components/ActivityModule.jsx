import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Editor from "@monaco-editor/react";
import { codeAPI } from "../services/api";
import "./CodeEditor.css";

// Language configurations for Monaco Editor
// Note: Judge0 uses "Main.java" as the filename, so Java classes must be named "Main"
const LANGUAGE_CONFIG = {
  python: {
    id: "python",
    label: "Python",
    defaultCode: '# Write your solution here\nprint("Hello, World!")\n',
  },
  javascript: {
    id: "javascript",
    label: "JavaScript",
    defaultCode: '// Write your solution here\nconsole.log("Hello, World!");\n',
  },
  java: {
    id: "java",
    label: "Java",
    defaultCode:
      'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        System.out.println("Hello, World!");\n    }\n}\n',
  },
  cpp: {
    id: "cpp",
    label: "C++",
    defaultCode:
      '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n',
  },
  c: {
    id: "c",
    label: "C",
    defaultCode:
      '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}\n',
  },
};

const ActivityModule = ({ activity, studentId, onBack, onSubmitSuccess }) => {
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [customInput, setCustomInput] = useState("");
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [activeTab, setActiveTab] = useState("output"); // 'output' or 'testcases'
  
  const editorRef = useRef(null);

  useEffect(() => {
    // Initialize code with starter code or default
    if (activity?.starter_code) {
      setCode(activity.starter_code);
    } else {
      const lang = activity?.programming_language || "python";
      setLanguage(lang);
      setCode(LANGUAGE_CONFIG[lang]?.defaultCode || "");
    }

    // Set language from activity
    if (activity?.programming_language) {
      setLanguage(activity.programming_language);
    }

    // Set first test case input as default
    if (activity?.test_cases?.length > 0) {
      setCustomInput(activity.test_cases[0].input || "");
    }
  }, [activity]);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure editor settings
    monaco.editor.defineTheme("customDark", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1e1e2e",
        "editor.foreground": "#cdd6f4",
        "editorLineNumber.foreground": "#6c7086",
        "editorCursor.foreground": "#f5e0dc",
        "editor.selectionBackground": "#45475a",
      },
    });
    monaco.editor.setTheme("customDark");
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput("");
    setTestResults(null);
    setActiveTab("output");

    try {
      const response = await codeAPI.runCode(
        activity.id,
        code,
        language,
        customInput
      );

      const data = response.data;

      if (data.error && !data.output) {
        setOutput(`Error:\n${data.error}`);
      } else {
        let outputText = data.output || "(No output)";
        if (data.error) {
          outputText += `\n\nStderr:\n${data.error}`;
        }
        if (data.time) {
          outputText += `\n\n⏱ Execution time: ${data.time}s`;
        }
        if (data.memory) {
          outputText += `\n💾 Memory: ${(data.memory / 1024).toFixed(2)} MB`;
        }
        setOutput(outputText);
      }
    } catch (error) {
      console.error("Run error:", error);
      setOutput(
        `Error: ${error.response?.data?.error || error.message || "Failed to run code"}`
      );
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmitCode = async () => {
    setIsSubmitting(true);
    setOutput("");
    setTestResults(null);
    setActiveTab("testcases");
    setShowResults(true);

    try {
      // Using sync submit for immediate feedback
      const response = await codeAPI.submitCodeSync(
        activity.id,
        studentId,
        code,
        language
      );

      const data = response.data;

      const result = {
        success: data.success,
        score: data.score,
        passed: data.passed,
        total: data.total,
        result: data.result,
        results: data.test_results || [],
      };
      
      setTestResults(result);

      // Notify parent of successful submission
      if (onSubmitSuccess) {
        onSubmitSuccess(data);
      }

      // Navigate to feedback page
      if (data.submission_id) {
        navigate(`/student/feedback/${data.submission_id}`);
      }
    } catch (error) {
      console.error("Submit error:", error);
      const errorResult = {
        success: false,
        score: 0,
        passed: 0,
        total: 0,
        result: "error",
        error:
          error.response?.data?.error || error.message || "Submission failed",
      };
      setTestResults(errorResult);
      setOutput(`Error: ${errorResult.error}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDifficultyClass = (difficulty) => {
    switch (difficulty) {
      case "easy":
        return "difficulty-easy";
      case "medium":
        return "difficulty-medium";
      case "hard":
        return "difficulty-hard";
      default:
        return "";
    }
  };

  const renderTestResults = () => {
    if (!testResults) return null;

    return (
      <div className="test-results-container">
        {/* Score Summary */}
        <div
          className={`score-summary ${testResults.success ? "passed" : "failed"}`}
        >
          <div className="score-icon">{testResults.success ? "✅" : "❌"}</div>
          <div className="score-details">
            <h3>{testResults.success ? "All Tests Passed!" : "Some Tests Failed"}</h3>
            <p>
              Score: <strong>{testResults.score}%</strong> ({testResults.passed}/
              {testResults.total} tests passed)
            </p>
          </div>
        </div>

        {/* Individual Test Results */}
        <div className="test-cases-list">
          {testResults.results?.map((test, index) => (
            <div
              key={index}
              className={`test-case-result ${test.passed ? "passed" : "failed"}`}
            >
              <div className="test-case-header">
                <span className="test-icon">{test.passed ? "✓" : "✗"}</span>
                <span className="test-name">Test Case {test.test_case}</span>
                <span className={`test-status ${test.passed ? "pass" : "fail"}`}>
                  {test.passed ? "PASS" : "FAIL"}
                </span>
              </div>

              <div className="test-case-details">
                {test.input && (
                  <div className="test-detail">
                    <label>Input:</label>
                    <pre>{test.input}</pre>
                  </div>
                )}
                <div className="test-detail">
                  <label>Expected Output:</label>
                  <pre>{test.expected_output}</pre>
                </div>
                <div className="test-detail">
                  <label>Your Output:</label>
                  <pre className={test.passed ? "" : "wrong"}>
                    {test.actual_output || "(No output)"}
                  </pre>
                </div>
                {test.error && (
                  <div className="test-detail error">
                    <label>Error:</label>
                    <pre>{test.error}</pre>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {testResults.error && (
          <div className="submission-error">
            <strong>Error:</strong> {testResults.error}
          </div>
        )}
      </div>
    );
  };

  if (!activity) {
    return <div className="activity-module">Loading activity...</div>;
  }

  return (
    <div className="activity-module">
      {/* Header */}
      <div className="activity-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Activities
        </button>
        <div className="activity-title-section">
          <h1>{activity.title}</h1>
          <span className={`difficulty-badge ${getDifficultyClass(activity.difficulty)}`}>
            {activity.difficulty}
          </span>
        </div>
        <div className="activity-meta">
          <span>⏱ {activity.time_limit} min</span>
          <span>👤 {activity.professor_name}</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="activity-content">
        {/* Left Panel - Problem Description */}
        <div className="problem-panel">
          <div className="problem-section">
            <h3>📋 Problem Description</h3>
            <p>{activity.description}</p>
          </div>

          <div className="problem-section">
            <h3>📝 Problem Statement</h3>
            <div className="problem-statement">{activity.problem_statement}</div>
          </div>

          {activity.test_cases?.length > 0 && (
            <div className="problem-section">
              <h3>🧪 Sample Test Cases</h3>
              {activity.test_cases.slice(0, 2).map((tc, idx) => (
                <div key={idx} className="sample-test-case">
                  <div className="test-case-label">Example {idx + 1}:</div>
                  {tc.input && (
                    <div className="test-io">
                      <strong>Input:</strong>
                      <pre>{tc.input}</pre>
                    </div>
                  )}
                  <div className="test-io">
                    <strong>Output:</strong>
                    <pre>{tc.expected_output}</pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Panel - Code Editor */}
        <div className="editor-panel">
          {/* Language Selector & Actions */}
          <div className="editor-toolbar">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              {Object.entries(LANGUAGE_CONFIG).map(([key, config]) => (
                <option key={key} value={key}>
                  {config.label}
                </option>
              ))}
            </select>

            <div className="action-buttons">
              <button
                className="run-btn"
                onClick={handleRunCode}
                disabled={isRunning || isSubmitting}
              >
                {isRunning ? "⏳ Running..." : "▶ Run"}
              </button>
              <button
                className="submit-btn"
                onClick={handleSubmitCode}
                disabled={isRunning || isSubmitting}
              >
                {isSubmitting ? "⏳ Submitting..." : "✓ Submit"}
              </button>
            </div>
          </div>

          {/* Monaco Editor */}
          <div className="code-editor-container">
            <Editor
              height="400px"
              language={language}
              value={code}
              onChange={(value) => setCode(value || "")}
              onMount={handleEditorDidMount}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: "on",
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 4,
                wordWrap: "on",
                padding: { top: 10, bottom: 10 },
              }}
              theme="vs-dark"
            />
          </div>

          {/* Custom Input for Run */}
          <div className="custom-input-section">
            <label>Custom Input (for Run):</label>
            <textarea
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              placeholder="Enter custom input here..."
              rows={3}
            />
          </div>

          {/* Output Section */}
          <div className="output-section">
            <div className="output-tabs">
              <button
                className={`tab-btn ${activeTab === "output" ? "active" : ""}`}
                onClick={() => setActiveTab("output")}
              >
                Output
              </button>
              <button
                className={`tab-btn ${activeTab === "testcases" ? "active" : ""}`}
                onClick={() => setActiveTab("testcases")}
              >
                Test Results {testResults && `(${testResults.passed}/${testResults.total})`}
              </button>
            </div>

            <div className="output-content">
              {activeTab === "output" ? (
                <pre className="output-display">
                  {output || "Run your code to see output here..."}
                </pre>
              ) : (
                <div className="test-results-display">
                  {testResults ? (
                    renderTestResults()
                  ) : (
                    <p className="no-results">
                      Submit your code to see test results...
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityModule;

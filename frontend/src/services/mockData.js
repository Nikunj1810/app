export const mockDoubts = [
  {
    id: "doubt_1",
    question: "What is the derivative of x^3 + 2x^2 - 5x + 3?",
    subject: "Math",
    type: "text",
    answer: {
      solution: "To find the derivative of f(x) = x³ + 2x² - 5x + 3, we'll use the power rule.\n\n**Step 1:** Apply the power rule to each term\n- d/dx(x³) = 3x²\n- d/dx(2x²) = 4x\n- d/dx(-5x) = -5\n- d/dx(3) = 0\n\n**Step 2:** Combine the results\nf'(x) = 3x² + 4x - 5\n\n**Therefore:** The derivative is **3x² + 4x - 5**",
      steps: [
        "Identify the function: f(x) = x³ + 2x² - 5x + 3",
        "Apply power rule to x³: d/dx(x³) = 3x²",
        "Apply power rule to 2x²: d/dx(2x²) = 4x",
        "Apply power rule to -5x: d/dx(-5x) = -5",
        "Derivative of constant 3 is 0",
        "Final answer: f'(x) = 3x² + 4x - 5"
      ]
    },
    timestamp: "2024-12-20T10:30:00Z",
    status: "answered"
  },
  {
    id: "doubt_2",
    question: "Explain photosynthesis process in plants",
    subject: "Biology",
    type: "text",
    answer: {
      solution: "Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen.\n\n**Chemical Equation:**\n6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂\n\n**Two Main Stages:**\n\n**1. Light Reactions (in thylakoids):**\n- Chlorophyll absorbs light energy\n- Water molecules split (H₂O → 2H⁺ + ½O₂ + 2e⁻)\n- ATP and NADPH are produced\n\n**2. Calvin Cycle (in stroma):**\n- CO₂ is fixed into organic molecules\n- Uses ATP and NADPH from light reactions\n- Produces glucose (C₆H₁₂O₆)\n\n**Significance:** Provides oxygen for breathing and food for all living organisms!",
      steps: [
        "Sunlight hits chlorophyll in plant leaves",
        "Light reactions occur in thylakoids",
        "Water splits to release oxygen",
        "Energy is captured as ATP and NADPH",
        "Calvin cycle uses CO₂ from air",
        "Glucose is produced as food storage"
      ]
    },
    timestamp: "2024-12-20T09:15:00Z",
    status: "answered"
  },
  {
    id: "doubt_3",
    question: "How do you balance the chemical equation: Al + O₂ → Al₂O₃?",
    subject: "Chemistry",
    type: "text",
    answer: {
      solution: "Let's balance the equation step by step:\n\n**Unbalanced:** Al + O₂ → Al₂O₃\n\n**Step 1:** Count atoms on each side\n- Left: 1 Al, 2 O\n- Right: 2 Al, 3 O\n\n**Step 2:** Balance aluminum first\nWe need 2 Al atoms on the left, so:\n2Al + O₂ → Al₂O₃\n\n**Step 3:** Balance oxygen\n- Right side has 3 O atoms\n- Left side needs 3 O atoms\n- Since O₂ gives 2 atoms, we need 3/2 O₂\n\n2Al + 3/2 O₂ → Al₂O₃\n\n**Step 4:** Remove fractions by multiplying by 2\n**Final balanced equation:** 4Al + 3O₂ → 2Al₂O₃",
      steps: [
        "Write the unbalanced equation",
        "Count atoms of each element",
        "Balance aluminum: 2Al + O₂ → Al₂O₃",
        "Balance oxygen: 2Al + 3/2O₂ → Al₂O₃",
        "Multiply by 2 to remove fractions",
        "Final: 4Al + 3O₂ → 2Al₂O₃"
      ]
    },
    timestamp: "2024-12-19T16:45:00Z",
    status: "answered"
  }
];

export const mockAIResponse = (question, subject, imageBase64 = null) => {
  // Simulate AI processing time
  return new Promise((resolve) => {
    setTimeout(() => {
      let response;
      
      if (imageBase64) {
        response = {
          solution: `I can see the ${subject.toLowerCase()} problem in your image. Based on the visual analysis:\n\n**Problem Analysis:**\nThe image shows a mathematical equation or diagram that I've analyzed.\n\n**Step-by-Step Solution:**\n\n**Step 1:** Identify the key elements in the image\n- Mathematical expressions or diagrams are clearly visible\n- The problem type appears to be related to ${subject}\n\n**Step 2:** Apply relevant formulas and concepts\n- Using standard ${subject.toLowerCase()} principles\n- Following systematic problem-solving approach\n\n**Step 3:** Calculate the solution\n- Performing necessary calculations\n- Verifying the result\n\n**Final Answer:** Based on the image analysis, the solution involves applying ${subject.toLowerCase()} concepts systematically.\n\n*Note: This is a mock response. The actual AI will provide detailed analysis of your uploaded image.*`,
          steps: [
            "Analyze the uploaded image",
            "Identify problem type and subject area", 
            "Extract key information from visual elements",
            "Apply appropriate mathematical/scientific concepts",
            "Perform step-by-step calculations",
            "Verify and present final answer"
          ]
        };
      } else {
        // Text-based responses
        const responses = {
          "math": {
            solution: `Let me solve this ${subject} problem step by step:\n\n**Given:** ${question}\n\n**Solution Process:**\n\n**Step 1:** Understand the problem\n- Identify what we need to find\n- List the given information\n\n**Step 2:** Choose the appropriate method\n- Apply relevant mathematical concepts\n- Use appropriate formulas\n\n**Step 3:** Solve systematically\n- Perform calculations step by step\n- Show all working clearly\n\n**Final Answer:** The solution demonstrates the systematic approach to solving this ${subject.toLowerCase()} problem.\n\n*This is a mock response demonstrating the AI's step-by-step problem-solving approach.*`,
            steps: [
              "Analyze the given problem",
              "Identify required mathematical concepts",
              "Set up the equation or approach",
              "Perform calculations systematically", 
              "Verify the solution",
              "Present final answer with explanation"
            ]
          },
          "default": {
            solution: `Here's a comprehensive explanation for your ${subject} question:\n\n**Topic:** ${question}\n\n**Detailed Explanation:**\n\n**Key Concepts:**\n- Understanding the fundamental principles\n- Connecting theory with practical applications\n- Breaking down complex ideas into simpler parts\n\n**Step-by-Step Breakdown:**\n1. **Foundation:** Start with basic concepts\n2. **Development:** Build upon these concepts\n3. **Application:** Show how to use this knowledge\n4. **Examples:** Provide relevant examples\n\n**Summary:** This ${subject.toLowerCase()} concept is important because it helps understand the underlying principles and their real-world applications.\n\n*This is a mock response. The actual AI will provide detailed, subject-specific explanations.*`,
            steps: [
              "Identify key concepts in the question",
              "Break down complex topics into parts",
              "Explain theoretical foundations",
              "Provide practical examples",
              "Connect concepts to real-world applications",
              "Summarize key takeaways"
            ]
          }
        };
        
        response = subject.toLowerCase() === "math" || subject.toLowerCase() === "mathematics" 
          ? responses.math 
          : responses.default;
      }
      
      resolve(response);
    }, 2000); // 2 second delay to simulate AI processing
  });
};

export const subjects = [
  "Mathematics",
  "Physics", 
  "Chemistry",
  "Biology",
  "English",
  "History",
  "Geography",
  "Computer Science",
  "Economics",
  "Other"
];
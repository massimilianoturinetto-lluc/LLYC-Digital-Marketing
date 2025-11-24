
import { GoogleGenAI, Type } from "@google/genai";
import { StrategyAnalysis, ScenarioConfig } from '../types';
import { MODEL_NAME } from '../constants';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

// Schema for the Strategy Analysis Phase 1
const analysisSchema = {
  type: Type.OBJECT,
  properties: {
    challengeStatement_A: { type: Type.STRING },
    challengeStatement_B: { type: Type.STRING },
    rumeltDiagnosis: { type: Type.STRING },
    rumeltGuidingPolicy: { type: Type.STRING },
    culturalTension: { type: Type.STRING },
    marketOpportunity: { type: Type.STRING },
    consumerInsight: { type: Type.STRING },
    behavioralJustification: { type: Type.STRING },
    keyAssumptions: {
      type: Type.ARRAY,
      items: { type: Type.STRING }
    },
    relevantMentalModels: {
      type: Type.ARRAY,
      items: { type: Type.STRING }
    },
    interpretation_challenger: { type: Type.STRING },
    interpretation_consultive: { type: Type.STRING },
    interpretation_mixed: { type: Type.STRING },
  },
  required: [
    "challengeStatement_A",
    "challengeStatement_B",
    "rumeltDiagnosis",
    "rumeltGuidingPolicy",
    "culturalTension",
    "marketOpportunity",
    "consumerInsight",
    "behavioralJustification",
    "keyAssumptions",
    "relevantMentalModels",
    "interpretation_challenger",
    "interpretation_consultive",
    "interpretation_mixed"
  ]
};

// Helper to convert file to Base64
const fileToPart = (file: File): Promise<any> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
        const result = reader.result as string;
        const base64String = result.split(',')[1];
        resolve({
            inlineData: {
                data: base64String,
                mimeType: file.type
            }
        });
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

export const generateStrategy = async (config: ScenarioConfig): Promise<StrategyAnalysis> => {
  try {
    const fileParts = await Promise.all(config.files.map(async (file) => {
      if (file.type === 'text/plain') {
          const text = await file.text();
          return { text: `\n[Attached File: ${file.name}]\n${text}\n` };
      }
      return await fileToPart(file);
    }));

    // Construct the user prompt as a JSON string per request
    const userPrompt = JSON.stringify({
      clientName: config.clientName,
      rawContext: config.rawContext,
      uploadedFiles: config.files.map(f => f.name).join(", ") || "None",
      opportunityType: config.opportunityType,
      mediaRole: config.mediaRole,
      digitalMaturity: config.digitalMaturity
    });

    const systemPrompt = `
You are “Maxicomm CSO”, an expert Chief Strategy Officer specialized in Digital Media, Full-Funnel Planning, Adtech, Measurement, GA4, Statistical Attribution, Programmatic, Meta, Google Marketing Platform, and data-driven efficiency.

Your ONLY mission in Phase 1 is:
Convert disorganized inputs (notes of a conversation, briefing, raw context, PDFs, documents, images or video) into a clear, structured, media-driven strategic formulation consisting of:

- Two strategic challenge statements
- A Rumelt-style Diagnosis (root cause)
- A Rumelt-style Guiding Policy (non-tactical direction)
- Strategic insights (cultural tension, market opportunity, consumer insight)
- Behavioral justification (behavioral economics)
- Key assumptions
- Relevant mental models
- Three interpretations: Challenger, Consultive, Mixed

This output is the INPUT for Phase 2 of the process.

PERSPECTIVE:
You ALWAYS think from the angle of:
Business → Digital Media → Data & Measurement → Adtech & Optimization → Execution Readiness
Never from generic business consulting or pure creativity.

MANDATORY JSON OUTPUT:
Your response must be a JSON object with EXACTLY these fields:

{
  "challengeStatement_A": "",
  "challengeStatement_B": "",
  "rumeltDiagnosis": "",
  "rumeltGuidingPolicy": "",
  "culturalTension": "",
  "marketOpportunity": "",
  "consumerInsight": "",
  "behavioralJustification": "",
  "keyAssumptions": [],
  "relevantMentalModels": [],
  "interpretation_challenger": "",
  "interpretation_consultive": "",
  "interpretation_mixed": ""
}

INSTRUCTIONS FOR EACH FIELD:

challengeStatement_A / challengeStatement_B:
Two different short, precise, strategically sharp formulations of the core challenge. They must be actionable from Digital Media & Adtech, not generic business puzzles.

rumeltDiagnosis:
Identify the single deepest obstacle at the intersection of:
- business problem
- customer problem
- data/measurement/adoption barriers
Keep it sharp, avoid fluff.

rumeltGuidingPolicy:
Define the broad strategic approach to address the root cause.  
Must be:
- executable through digital media & data
- aligned with the client’s digital maturity
- realistic in investment
- NOT a tactical plan
- NOT creative execution

culturalTension:
A cultural or social force affecting the category or consumer behavior.

marketOpportunity:
A concrete opportunity based on demand, gaps, or competitive landscape, from a media/data viewpoint.

consumerInsight:
A psychologically deep point revealing motivation, tension, or barrier in the consumer decision journey.

behavioralJustification:
Explain why the Guiding Policy works using behavioral economics (mere exposure, cognitive load, loss aversion, choice architecture, consistency, scarcity, etc.)

keyAssumptions:
List the assumptions that, if wrong, would break the strategy.

relevantMentalModels:
Include Rumelt’s Sources of Power (Leverage, Focus, Chain-Link), or similar strategic frameworks applied in media.

interpretation_challenger:
A direct, hard, almost uncomfortable interpretation that challenges weak thinking in the brief.

interpretation_consultive:
A softer, structured, advisory interpretation.

interpretation_mixed:
Balanced between urgency and empathy.

RESTRICTIONS:
- Do NOT propose creative concepts or messages.
- Do NOT propose detailed media plans or channels.
- Do NOT propose large investments or organizational restructures.
- Do NOT mention specific ad platforms or tools by name.
- Everything must be digitally actionable and measurable.
- All content must be in Spanish.
- All content must strictly follow the JSON format.
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: [
          { text: userPrompt },
          ...fileParts
      ],
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        systemInstruction: systemPrompt,
        thinkingConfig: { thinkingBudget: 2048 } // Increased budget for complex analysis
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from AI");
    
    return JSON.parse(text) as StrategyAnalysis;

  } catch (error) {
    console.error("Gemini API Error:", error);
    throw error;
  }
};

const RATING_LEVELS = { "High": 4, "Moderate": 3, "Low": 2, "Very low": 1 };
const RATING_LEVELS_INV = { 4: "High", 3: "Moderate", 2: "Low", 1: "Very low" };

function calculateDirectRating(row) {
    if (!row.Direct_estimate || row.Direct_estimate === '.') {
        return null;
    }

    let downgrades = 0;
    const domains = ["ROB", "Inconsistency", "Indirectness", "Publication_bias"];
    domains.forEach(domain => {
        if (row[domain] === "Serious") {
            downgrades += 1;
        } else if (row[domain] === "Very serious") {
            downgrades += 2;
        }
    });

    const finalLevel = Math.max(1, 4 - downgrades);
    return RATING_LEVELS_INV[finalLevel];
}

/**
 * NEW: Calculates the certainty of evidence for indirect comparisons.
 * This is a direct translation of the logic in `GRADE Evaluation Interactive Tool.py`.
 */
function calculateCertaintyOfEvidence(allRows) {
    // Step 1: Find the most important "bridge" treatments based on total sample size.
    const armSamples = {};
    allRows.forEach(row => {
        const sampleSize = parseFloat(row.Sample_size);
        if (!isNaN(sampleSize)) {
            armSamples[row.Arm_1] = (armSamples[row.Arm_1] || 0) + sampleSize;
            armSamples[row.Arm_2] = (armSamples[row.Arm_2] || 0) + sampleSize;
        }
    });

    // Sort arms by total sample size to find the top contributors (bridges)
    const sortedArms = Object.keys(armSamples).sort((a, b) => armSamples[b] - armSamples[a]);
    const topBridges = sortedArms.slice(0, 2); // Take top 2 as primary bridges

    // Step 2: Create a lookup map for direct ratings for faster access.
    const directRatingMap = new Map();
    allRows.forEach(row => {
        if (row.Direct_rating_without_imprecision) {
            directRatingMap.set(`${row.Arm_1}|${row.Arm_2}`, row.Direct_rating_without_imprecision);
            directRatingMap.set(`${row.Arm_2}|${row.Arm_1}`, row.Direct_rating_without_imprecision);
        }
    });

    // Step 3: Define a function to get the certainty for a single arm.
    function getCertainty(arm) {
        // Find the direct rating of the connection between this arm and a top bridge.
        for (const bridge of topBridges) {
            if (arm === bridge) continue; // An arm can't bridge to itself
            const rating = directRatingMap.get(`${arm}|${bridge}`);
            if (rating) {
                return rating;
            }
        }
        // If no direct connection to a top bridge is found, default to "Low" as per original logic.
        return "Low";
    }

    // Step 4: Apply this logic to each row that has an indirect estimate.
    allRows.forEach(row => {
        if (row.Indirect_estimate && row.Indirect_estimate !== '.') {
            row.Certainty_of_evidence_for_arm1 = getCertainty(row.Arm_1);
            row.Certainty_of_evidence_for_arm2 = getCertainty(row.Arm_2);
            // Certainty_of_evidence_for_arm3 is not dynamically calculated in the same way,
            // so we leave it as is from the initial Python run.
        } else {
            row.Certainty_of_evidence_for_arm1 = null;
            row.Certainty_of_evidence_for_arm2 = null;
        }
    });
}


/**
 * Calculates the indirect evidence rating.
 * This now uses the dynamically calculated Certainty of evidence.
 */
function calculateIndirectRating(row) {
    if (!row.Indirect_estimate || row.Indirect_estimate === '.') {
        return null;
    }

    const cert1Level = RATING_LEVELS[row.Certainty_of_evidence_for_arm1] || 2; // Default to Low
    const cert2Level = RATING_LEVELS[row.Certainty_of_evidence_for_arm2] || 2; // Default to Low

    let lowestPathLevel = Math.min(cert1Level, cert2Level);

    // Apply intransitivity downgrade
    if (row.Intransitivity === "Serious") {
        lowestPathLevel -= 1;
    } else if (row.Intransitivity === "Very serious") {
        lowestPathLevel -= 2;
    }

    const finalLevel = Math.max(1, lowestPathLevel);
    return RATING_LEVELS_INV[finalLevel];
}


/**
 * Determines the higher rating between direct and indirect evidence.
 */
function getHigherRating(directRating, indirectRating) {
    const directLevel = RATING_LEVELS[directRating] || 0;
    const indirectLevel = RATING_LEVELS[indirectRating] || 0;

    if (directLevel === 0 && indirectLevel === 0) return null;

    return directLevel >= indirectLevel ? directRating : indirectRating;
}

/**
 * Determines which evidence type to use for the final rating.
 */
function determineEvidenceType(row) {
    const hasDirect = row.Direct_rating_without_imprecision !== null;
    const hasIndirect = row.Indirect_rating_without_imprecision !== null;

    if (hasDirect && hasIndirect) {
        if (row.Incoherence === "Serious" || row.Incoherence === "Very serious") {
            const directLevel = RATING_LEVELS[row.Direct_rating_without_imprecision] || 0;
            const indirectLevel = RATING_LEVELS[row.Indirect_rating_without_imprecision] || 0;
            return directLevel >= indirectLevel ? "direct" : "indirect";
        }
        return "network";
    } else if (hasDirect) {
        return "direct";
    } else if (hasIndirect) {
        return "indirect";
    }
    return "unknown";
}


/**
 * Calculates the final rating after all downgrades.
 */
function calculateFinalRating(row) {
    const evidenceType = row.Evidence_type_for_final_rating;
    let baseRating;
    let downgrades = 0;

    switch (evidenceType) {
        case 'network':
            baseRating = row.Higher_rating_of_direct_and_indirect_without_imprecision;
            if (row.Incoherence === "Serious") downgrades += 1;
            if (row.Incoherence === "Very serious") downgrades += 2;
            break;
        case 'direct':
            baseRating = row.Direct_rating_without_imprecision;
            break;
        case 'indirect':
            baseRating = row.Indirect_rating_without_imprecision;
            break;
        default:
            return row.Final_rating;
    }

    if (row.Imprecision === "Serious") downgrades += 1;
    if (row.Imprecision === "Very serious") downgrades += 2;
    if (row.Imprecision === "Extremely serious") downgrades += 3;

    const baseLevel = RATING_LEVELS[baseRating] || 0;
    if (baseLevel === 0) return null;

    const finalLevel = Math.max(1, baseLevel - downgrades);
    return RATING_LEVELS_INV[finalLevel];
}

/**
 * Generates the reason text for the final rating.
 */
function getFinalRatingReason(row) {
    const evidenceType = row.Evidence_type_for_final_rating;
    const imprecisionText = `Imprecision was rated as ${row.Imprecision || 'Not serious'}.`;
    let reason = "";

    switch (evidenceType) {
        case 'network':
            reason = "NMA estimate was used because direct and indirect evidence were consistent. ";
            if (row.Incoherence === "Serious" || row.Incoherence === "Very serious") {
                reason += `The rating was further downgraded due to significant incoherence (${row.Incoherence}).`;
            }
            break;
        case 'direct':
            reason = `Direct estimate was used because ${row.Indirect_rating_without_imprecision === null ? 'no indirect evidence was available' : 'of significant incoherence and direct evidence had higher certainty'}. `;
            break;
        case 'indirect':
            reason = `Indirect estimate was used because ${row.Direct_rating_without_imprecision === null ? 'no direct evidence was available' : 'of significant incoherence and indirect evidence had higher certainty'}. `;
            break;
        default:
            reason = "Final rating was determined based on available evidence. ";
    }
    return reason + imprecisionText;
}


/**
 * Main function to run all calculations in sequence for the entire dataset.
 * The order of these calculations is critical.
 */
function updateAllCalculations(data) {
    // 1. Calculate direct rating for all rows first.
    data.forEach(row => {
        row.Direct_rating_without_imprecision = calculateDirectRating(row);
    });

    // 2. Calculate certainty of evidence for all rows based on the new direct ratings.
    calculateCertaintyOfEvidence(data);

    // 3. Now, iterate again to calculate the remaining dependent fields.
    data.forEach(row => {
        row.Indirect_rating_without_imprecision = calculateIndirectRating(row);
        
        row.Higher_rating_of_direct_and_indirect_without_imprecision = getHigherRating(
            row.Direct_rating_without_imprecision,
            row.Indirect_rating_without_imprecision
        );
        
        row.Evidence_type_for_final_rating = determineEvidenceType(row);
        
        row.Final_rating = calculateFinalRating(row);
        
        row.Final_rating_reason = getFinalRatingReason(row);
    });

    return data;
}

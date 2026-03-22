// =============================================================================
// Migration: activation_condition / activation_decision_date → lifecycle names
// Version: v2.25.0 (U12)
// =============================================================================
// Both operations are IDEMPOTENT — safe to run multiple times.
// The application (from_dict fallbacks) works correctly before and after this
// migration, so there is no strict ordering requirement with the code deploy.
// =============================================================================

// 1. Rename activation_condition → trigger_condition
MATCH (r:Risk) WHERE r.activation_condition IS NOT NULL
SET r.trigger_condition = r.activation_condition
REMOVE r.activation_condition;

// 2. Rename activation_decision_date → acceptance_date
MATCH (r:Risk) WHERE r.activation_decision_date IS NOT NULL
SET r.acceptance_date = r.activation_decision_date
REMOVE r.activation_decision_date;

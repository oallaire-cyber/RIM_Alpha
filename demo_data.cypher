// Risk Influence Map - Demo Data
// Sample risks and influences for demonstration purposes
// Load this file in Neo4j Browser to populate the database

// Clear existing data (optional - comment out if you want to keep existing data)
MATCH (n) DETACH DELETE n;

// Create Cyber Security Risks
CREATE (r1:Risk {
    name: 'Phishing Attack',
    category: 'Cyber',
    probability: 8,
    impact: 7,
    score: 56,
    status: 'Active',
    description: 'Risk of employees clicking malicious email links leading to credential theft'
});

CREATE (r2:Risk {
    name: 'Credential Compromise',
    category: 'Cyber',
    probability: 6,
    impact: 9,
    score: 54,
    status: 'Active',
    description: 'Unauthorized access to systems through stolen or compromised credentials'
});

CREATE (r3:Risk {
    name: 'Lateral Movement',
    category: 'Cyber',
    probability: 5,
    impact: 8,
    score: 40,
    status: 'Monitored',
    description: 'Attacker moving through the network after initial compromise'
});

CREATE (r4:Risk {
    name: 'Data Exfiltration',
    category: 'Cyber',
    probability: 4,
    impact: 10,
    score: 40,
    status: 'Active',
    description: 'Unauthorized transfer of sensitive data outside the organization'
});

CREATE (r5:Risk {
    name: 'Ransomware Deployment',
    category: 'Cyber',
    probability: 5,
    impact: 9,
    score: 45,
    status: 'Active',
    description: 'Encryption of critical systems and data with ransom demands'
});

// Create Operational Risks
CREATE (r6:Risk {
    name: 'System Downtime',
    category: 'Operational',
    probability: 6,
    impact: 8,
    score: 48,
    status: 'Active',
    description: 'Critical systems unavailable impacting business operations'
});

CREATE (r7:Risk {
    name: 'Supply Chain Disruption',
    category: 'Operational',
    probability: 5,
    impact: 7,
    score: 35,
    status: 'Monitored',
    description: 'Interruption in supply chain affecting delivery and operations'
});

CREATE (r8:Risk {
    name: 'Data Loss',
    category: 'Operational',
    probability: 4,
    impact: 9,
    score: 36,
    status: 'Active',
    description: 'Permanent loss of critical business data'
});

// Create Strategic Risks
CREATE (r9:Risk {
    name: 'Reputation Damage',
    category: 'Reputation',
    probability: 7,
    impact: 9,
    score: 63,
    status: 'Active',
    description: 'Negative public perception impacting brand value and customer trust'
});

CREATE (r10:Risk {
    name: 'Market Share Loss',
    category: 'Strategic',
    probability: 6,
    impact: 8,
    score: 48,
    status: 'Monitored',
    description: 'Decline in competitive position and market share'
});

// Create Compliance Risks
CREATE (r11:Risk {
    name: 'GDPR Violation',
    category: 'Compliance',
    probability: 5,
    impact: 8,
    score: 40,
    status: 'Active',
    description: 'Non-compliance with GDPR regulations leading to fines and penalties'
});

CREATE (r12:Risk {
    name: 'Regulatory Audit Failure',
    category: 'Compliance',
    probability: 4,
    impact: 7,
    score: 28,
    status: 'Monitored',
    description: 'Failure to meet regulatory requirements during audit'
});

// Create Financial Risks
CREATE (r13:Risk {
    name: 'Financial Loss',
    category: 'Financial',
    probability: 7,
    impact: 9,
    score: 63,
    status: 'Active',
    description: 'Direct financial impact from security incidents or operational failures'
});

CREATE (r14:Risk {
    name: 'Insurance Premium Increase',
    category: 'Financial',
    probability: 8,
    impact: 5,
    score: 40,
    status: 'Monitored',
    description: 'Rising insurance costs due to increased risk profile'
});

// Create HR Risks
CREATE (r15:Risk {
    name: 'Key Personnel Loss',
    category: 'HR',
    probability: 6,
    impact: 7,
    score: 42,
    status: 'Active',
    description: 'Loss of critical staff impacting operations and knowledge retention'
});

// Create Influences - Cyber Attack Chain
MATCH (r1:Risk {name: 'Phishing Attack'})
MATCH (r2:Risk {name: 'Credential Compromise'})
CREATE (r1)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 9,
    description: 'Successful phishing directly leads to credential compromise'
}]->(r2);

MATCH (r2:Risk {name: 'Credential Compromise'})
MATCH (r3:Risk {name: 'Lateral Movement'})
CREATE (r2)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 8,
    description: 'Compromised credentials enable lateral movement within network'
}]->(r3);

MATCH (r3:Risk {name: 'Lateral Movement'})
MATCH (r4:Risk {name: 'Data Exfiltration'})
CREATE (r3)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 7,
    description: 'Lateral movement increases access to sensitive data'
}]->(r4);

MATCH (r3:Risk {name: 'Lateral Movement'})
MATCH (r5:Risk {name: 'Ransomware Deployment'})
CREATE (r3)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 8,
    description: 'Wider network access enables more effective ransomware deployment'
}]->(r5);

// Create Influences - Operational Impacts
MATCH (r5:Risk {name: 'Ransomware Deployment'})
MATCH (r6:Risk {name: 'System Downtime'})
CREATE (r5)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 9,
    description: 'Ransomware encryption causes immediate system downtime'
}]->(r6);

MATCH (r6:Risk {name: 'System Downtime'})
MATCH (r7:Risk {name: 'Supply Chain Disruption'})
CREATE (r6)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 7,
    description: 'System unavailability disrupts supply chain operations'
}]->(r7);

MATCH (r5:Risk {name: 'Ransomware Deployment'})
MATCH (r8:Risk {name: 'Data Loss'})
CREATE (r5)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 6,
    description: 'Ransomware can lead to data loss if backups are compromised'
}]->(r8);

// Create Influences - Strategic and Reputational
MATCH (r4:Risk {name: 'Data Exfiltration'})
MATCH (r9:Risk {name: 'Reputation Damage'})
CREATE (r4)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 9,
    description: 'Data breach incidents severely damage public trust and reputation'
}]->(r9);

MATCH (r6:Risk {name: 'System Downtime'})
MATCH (r9:Risk {name: 'Reputation Damage'})
CREATE (r6)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 7,
    description: 'Extended outages harm customer satisfaction and reputation'
}]->(r9);

MATCH (r9:Risk {name: 'Reputation Damage'})
MATCH (r10:Risk {name: 'Market Share Loss'})
CREATE (r9)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 8,
    description: 'Damaged reputation drives customers to competitors'
}]->(r10);

// Create Influences - Compliance
MATCH (r4:Risk {name: 'Data Exfiltration'})
MATCH (r11:Risk {name: 'GDPR Violation'})
CREATE (r4)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 9,
    description: 'Data breaches trigger GDPR violation and reporting requirements'
}]->(r11);

MATCH (r11:Risk {name: 'GDPR Violation'})
MATCH (r12:Risk {name: 'Regulatory Audit Failure'})
CREATE (r11)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 7,
    description: 'GDPR violations increase likelihood of failing regulatory audits'
}]->(r12);

// Create Influences - Financial
MATCH (r11:Risk {name: 'GDPR Violation'})
MATCH (r13:Risk {name: 'Financial Loss'})
CREATE (r11)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 8,
    description: 'GDPR fines can reach millions of euros'
}]->(r13);

MATCH (r5:Risk {name: 'Ransomware Deployment'})
MATCH (r13:Risk {name: 'Financial Loss'})
CREATE (r5)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 9,
    description: 'Ransom payments and recovery costs create direct financial losses'
}]->(r13);

MATCH (r6:Risk {name: 'System Downtime'})
MATCH (r13:Risk {name: 'Financial Loss'})
CREATE (r6)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 8,
    description: 'Downtime results in lost revenue and productivity'
}]->(r13);

MATCH (r13:Risk {name: 'Financial Loss'})
MATCH (r14:Risk {name: 'Insurance Premium Increase'})
CREATE (r13)-[:INFLUENCES {
    type: 'TRIGGERS',
    strength: 7,
    description: 'Claims and incidents lead to higher insurance premiums'
}]->(r14);

// Create Influences - HR
MATCH (r6:Risk {name: 'System Downtime'})
MATCH (r15:Risk {name: 'Key Personnel Loss'})
CREATE (r6)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 6,
    description: 'Repeated incidents can lead to employee frustration and turnover'
}]->(r15);

MATCH (r9:Risk {name: 'Reputation Damage'})
MATCH (r15:Risk {name: 'Key Personnel Loss'})
CREATE (r9)-[:INFLUENCES {
    type: 'AMPLIFIES',
    strength: 6,
    description: 'Reputation issues make it harder to retain and attract talent'
}]->(r15);

// Create some Correlation relationships
MATCH (r1:Risk {name: 'Phishing Attack'})
MATCH (r7:Risk {name: 'Supply Chain Disruption'})
CREATE (r1)-[:INFLUENCES {
    type: 'CORRELATES',
    strength: 5,
    description: 'Both often occur during organizational stress periods'
}]->(r7);

MATCH (r10:Risk {name: 'Market Share Loss'})
MATCH (r13:Risk {name: 'Financial Loss'})
CREATE (r10)-[:INFLUENCES {
    type: 'CORRELATES',
    strength: 8,
    description: 'Market share loss directly correlates with revenue decline'
}]->(r13);

// Create some Mitigation relationships
MATCH (r12:Risk {name: 'Regulatory Audit Failure'})
MATCH (r11:Risk {name: 'GDPR Violation'})
CREATE (r12)-[:INFLUENCES {
    type: 'MITIGATES',
    strength: 6,
    description: 'Proactive audit preparation reduces GDPR violation risk'
}]->(r11);

// Verification query - Return summary statistics
MATCH (r:Risk)
WITH count(r) as risk_count
MATCH ()-[i:INFLUENCES]->()
WITH risk_count, count(i) as influence_count
RETURN risk_count as total_risks, influence_count as total_influences;

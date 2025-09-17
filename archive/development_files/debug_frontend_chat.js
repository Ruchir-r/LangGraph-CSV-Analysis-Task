// Debug script to simulate frontend chat API call
const fetch = require('node-fetch');

// Simulate what the frontend should send
async function testFrontendChatCall() {
    console.log('🔍 Testing Frontend Chat API Call...\n');
    
    // Simulate the files array that frontend might have
    const mockFiles = [
        { file_id: 19, id: 19, filename: 'sales_nov_2024.csv' }, // Both snake_case and camelCase
        { file_id: 17, id: 17, filename: 'sales_dec_2024.csv' }
    ];
    
    // Extract file IDs like the frontend does
    const fileIds = mockFiles.map(file => file.id).filter(id => id);
    console.log('File IDs being sent:', fileIds);
    
    // Test the API call
    const response = await fetch('http://localhost:8000/api/v2/chat/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: "What files do I have? Tell me about my data.",
            session_id: "frontend-debug",
            file_context: fileIds,
            enable_workflow: false
        }),
    });
    
    const data = await response.json();
    console.log('\n✅ API Response:');
    console.log(data.response);
    console.log('\nWorkflow initiated:', data.workflow_initiated);
    console.log('Analysis scope:', data.analysis_scope);
}

testFrontendChatCall().catch(console.error);
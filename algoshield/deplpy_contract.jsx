import React, { useState } from 'react';
import axios from 'axios';

const DeployContract = () => {
    const [response, setResponse] = useState(null);

    const handleDeploy = async () => {
        try {
            const res = await axios.post('http://localhost:8000/deploy-contract/');
            setResponse(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div>
            <button onClick={handleDeploy}>Deploy Contract</button>
            {response && (
                <div>
                    <p>App ID: {response.app_id}</p>
                    <p>Transaction ID: {response.transaction_id}</p>
                    <pre>{JSON.stringify(response.compiled_approval, null, 2)}</pre>
                    <pre>{JSON.stringify(response.compiled_clear, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default DeployContract;

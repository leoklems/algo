import React, { useState } from 'react';
import axios from 'axios';

const AssignRoom = () => {
    const [amount, setAmount] = useState('');
    const [appId, setAppId] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:8000/assign-room/', {
                amount,
                app_id: appId
            });
            setResponse(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input 
                    type="number" 
                    value={amount} 
                    onChange={(e) => setAmount(e.target.value)} 
                    placeholder="Enter amount" 
                />
                <input 
                    type="text" 
                    value={appId} 
                    onChange={(e) => setAppId(e.target.value)} 
                    placeholder="Enter app ID" 
                />
                <button type="submit">Assign Room</button>
            </form>
            {response && <p>Transaction ID: {response.transaction_id}</p>}
        </div>
    );
};

export default AssignRoom;

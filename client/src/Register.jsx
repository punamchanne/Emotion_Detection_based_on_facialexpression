import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from './api';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [faceImage, setFaceImage] = useState(null);
    const [error, setError] = useState('');
    const [status, setStatus] = useState('');
    const navigate = useNavigate();

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [cameraActive, setCameraActive] = useState(false);

    useEffect(() => {
        startCamera();
        return () => stopCamera();
    }, []);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setCameraActive(true);
            }
        } catch (err) {
            console.error("Camera access error:", err);
            setError("Could not access camera for face capture.");
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        }
    };

    const captureFace = () => {
        if (!videoRef.current || !canvasRef.current) return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg');
        setFaceImage(dataUrl);
        setStatus('Face captured successfully!');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!faceImage) {
            setError('Please capture your face before registering.');
            return;
        }
        try {
            const response = await api.post('/register', {
                username,
                password,
                confirm_password: confirmPassword,
                face_image: faceImage
            });
            if (response.data.success) {
                navigate('/login');
            }
        } catch (err) {
            setError(err.response?.data?.message || 'Registration failed');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-box" style={{ maxWidth: '800px' }}>
                <div className="auth-header">
                    <h2>Create Account</h2>
                    <p>Join us to discover music and coffee that matches your vibe</p>
                </div>

                {error && <div className="alert alert-error">{error}</div>}
                {status && <div className="alert alert-success">{status}</div>}

                <div className="registration-content" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                className="form-control"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Password</label>
                            <input
                                type="password"
                                className="form-control"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input
                                type="password"
                                className="form-control"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button type="submit" className="btn-primary" disabled={!faceImage}>Sign Up</button>
                    </form>

                    <div className="face-capture-section" style={{ textAlign: 'center' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>Face Registration</label>
                        <div className="video-preview" style={{ 
                            width: '100%', 
                            aspectRatio: '4/3', 
                            background: '#000', 
                            borderRadius: '12px',
                            overflow: 'hidden',
                            position: 'relative'
                        }}>
                            <video 
                                ref={videoRef} 
                                autoPlay 
                                muted 
                                playsInline 
                                style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
                            />
                            {faceImage && (
                                <img 
                                    src={faceImage} 
                                    style={{ 
                                        position: 'absolute', 
                                        top: 0, 
                                        left: 0, 
                                        width: '100%', 
                                        height: '100%', 
                                        objectFit: 'cover',
                                        border: '4px solid #00c853',
                                        transform: 'scaleX(-1)'
                                    }} 
                                    alt="Captured face" 
                                />
                            )}
                        </div>
                        <canvas ref={canvasRef} style={{ display: 'none' }} />
                        <button 
                            type="button" 
                            className="btn-secondary" 
                            onClick={captureFace}
                            style={{ marginTop: '1rem', width: '100%' }}
                        >
                            {faceImage ? 'Retake Face' : 'Capture Face'}
                        </button>
                    </div>
                </div>

                <div className="auth-footer">
                    <p>Already have an account? <Link to="/login">Sign In</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Register;

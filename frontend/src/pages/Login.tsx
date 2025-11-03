import { useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { loginUser } from "../api";
import { setAuthToken } from "../api/client";
import { useAuth } from "../context/AuthContext";

interface LoginForm {
  email: string;
  password: string;
}

export const LoginPage: React.FC = () => {
  const { register, handleSubmit } = useForm<LoginForm>();
  const [isLoading, setLoading] = useState(false);
  const auth = useAuth();
  const navigate = useNavigate();

  const onSubmit: SubmitHandler<LoginForm> = async (data) => {
    setLoading(true);
    try {
      const token = await loginUser(data.email, data.password);
      setAuthToken(token.access_token);
      auth.login(token.access_token, { email: data.email });
      toast.success("Welcome back!");
      navigate("/", { replace: true });
    } catch (error) {
      console.error(error);
      toast.error("Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <div className="auth__panel">
        <h1>GeM Bid Analyzer</h1>
        <p className="auth__subtitle">Centralize your GeM tenders, decode compliance, and collaborate securely.</p>
        <form className="auth__form" onSubmit={handleSubmit(onSubmit)}>
          <label>
            Email address
            <input type="email" placeholder="you@company.in" {...register("email", { required: true })} />
          </label>
          <label>
            Password
            <input type="password" placeholder="????????" {...register("password", { required: true })} />
          </label>
          <button className="btn" type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="auth__cta">
          New to the platform? <Link to="/register">Create an account</Link>
        </p>
      </div>
      <div className="auth__hero">
        <div className="auth__glass">
          <h2>Bid faster, smarter</h2>
          <ul>
            <li>Summaries of technical specs, BOQ, ATC, eligibility, and milestones</li>
            <li>Download branded reports ready for internal circulation</li>
            <li>Email zipped bundles to partner OEMs straight from the platform</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

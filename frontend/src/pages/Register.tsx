import { useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { registerUser } from "../api";

interface RegisterForm {
  email: string;
  password: string;
  fullName?: string;
  organization?: string;
}

export const RegisterPage: React.FC = () => {
  const { register, handleSubmit } = useForm<RegisterForm>();
  const [isLoading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit: SubmitHandler<RegisterForm> = async (data) => {
    setLoading(true);
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        full_name: data.fullName,
        organization: data.organization
      });
      toast.success("Account created. Sign in to continue.");
      navigate("/login");
    } catch (error) {
      console.error(error);
      toast.error("Unable to register. Email may already exist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth">
      <div className="auth__panel">
        <h1>Create account</h1>
        <p className="auth__subtitle">Set up your workspace to start analyzing GeM tenders.</p>
        <form className="auth__form" onSubmit={handleSubmit(onSubmit)}>
          <label>
            Full name
            <input type="text" placeholder="Rohit Sharma" {...register("fullName")} />
          </label>
          <label>
            Organization
            <input type="text" placeholder="ABC Infra Pvt Ltd" {...register("organization")} />
          </label>
          <label>
            Work email
            <input type="email" placeholder="you@company.in" {...register("email", { required: true })} />
          </label>
          <label>
            Password
            <input type="password" placeholder="Minimum 8 characters" {...register("password", { required: true })} />
          </label>
          <button className="btn" type="submit" disabled={isLoading}>
            {isLoading ? "Creating..." : "Create account"}
          </button>
        </form>
        <p className="auth__cta">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
      <div className="auth__hero">
        <div className="auth__glass">
          <h2>Enterprise-grade security</h2>
          <ul>
            <li>Role-based access so bid teams stay in control</li>
            <li>Audit log of every document upload and export</li>
            <li>Straightforward SMTP integration for your mail relay</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

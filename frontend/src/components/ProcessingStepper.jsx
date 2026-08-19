import { Check, X, Loader } from 'lucide-react';

export default function ProcessingStepper({ steps, currentStep, error }) {
  return (
    <div className="stepper" aria-label="Processing steps">
      {steps.map((label, index) => {
        let status = 'pending';
        if (error && index === currentStep) status = 'error';
        else if (index < currentStep) status = 'completed';
        else if (index === currentStep) status = 'active';

        return (
          <div key={index} className={`stepper__step ${status}`} aria-current={status === 'active' ? 'step' : undefined}>
            <div className="stepper__indicator">
              {status === 'completed' && <Check size={14} />}
              {status === 'error' && <X size={14} />}
              {status === 'active' && !error && null /* spinner via CSS */}
              {status === 'pending' && <span>{index + 1}</span>}
            </div>
            <span>{label}</span>
          </div>
        );
      })}
    </div>
  );
}

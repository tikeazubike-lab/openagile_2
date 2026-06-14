import { useReducer } from "react";

const initialState = {
    step: 1,
    fields: { name: "", email: "", plan: "", cardNumber: "" },
    errors: {},
    submitted: false,
};

function formReducer(state, action) {
    switch (action.type) {
        case "UPDATE_FIELD":
            return {
                ...state,
                fields: { ...state.fields, [action.field]: action.value },
                errors: { ...state.errors, [action.field]: "" }, // clear error on edit
            };
        case "SET_ERRORS":
            return { ...state, errors: action.errors };
        case "NEXT_STEP":
            return { ...state, step: state.step + 1 };
        case "PREV_STEP":
            return { ...state, step: state.step - 1 };
        case "SUBMIT":
            return { ...state, submitted: true };
        default:
            return state;
    }
}

function validate(step, fields) {
    const errors = {};
    if (step === 1 && !fields.name) errors.name = "Required";
    if (step === 1 && !fields.email.includes("@")) errors.email = "Invalid email";
    if (step === 2 && !fields.plan) errors.plan = "Select a plan";
    return errors;
}

export default function FormWizard() {
    const [state, dispatch] = useReducer(formReducer, initialState);
    const { step, fields, errors, submitted } = state;

    const handleNext = () => {
        const errs = validate(step, fields);
        if (Object.keys(errs).length) {
            dispatch({ type: "SET_ERRORS", errors: errs });
        } else {
            dispatch({ type: "NEXT_STEP" });
        }
    };

    if (submitted) return <h2>✅ Registration complete!</h2>;

    return (
        <div style={{ fontFamily: "sans-serif", padding: 20, maxWidth: 400 }}>
            <h2>Step {step} of 3</h2>

            {step === 1 && (
                <>
                    <div>
                        <input
                            placeholder="Name"
                            value={fields.name}
                            onChange={e => dispatch({ type: "UPDATE_FIELD", field: "name", value: e.target.value })}
                        />
                        {errors.name && <span style={{ color: "red" }}>{errors.name}</span>}
                    </div>
                    <div>
                        <input
                            placeholder="Email"
                            value={fields.email}
                            onChange={e => dispatch({ type: "UPDATE_FIELD", field: "email", value: e.target.value })}
                        />
                        {errors.email && <span style={{ color: "red" }}>{errors.email}</span>}
                    </div>
                </>
            )}

            {step === 2 && (
                <div>
                    {["Basic", "Pro", "Enterprise"].map(p => (
                        <label key={p} style={{ display: "block" }}>
                            <input
                                type="radio"
                                name="plan"
                                value={p}
                                checked={fields.plan === p}
                                onChange={e => dispatch({ type: "UPDATE_FIELD", field: "plan", value: e.target.value })}
                            />
                            {p}
                        </label>
                    ))}
                    {errors.plan && <span style={{ color: "red" }}>{errors.plan}</span>}
                </div>
            )}

            {step === 3 && (
                <div>
                    <p>Review: <strong>{fields.name}</strong> — {fields.plan} plan</p>
                    <input
                        placeholder="Card number"
                        value={fields.cardNumber}
                        onChange={e => dispatch({ type: "UPDATE_FIELD", field: "cardNumber", value: e.target.value })}
                    />
                </div>
            )}

            <div style={{ marginTop: 10 }}>
                {step > 1 && <button onClick={() => dispatch({ type: "PREV_STEP" })}>Back</button>}
                {step < 3 && <button onClick={handleNext}>Next</button>}
                {step === 3 && <button onClick={() => dispatch({ type: "SUBMIT" })}>Submit</button>}
            </div>
        </div>
    );
}
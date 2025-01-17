/**
 * A wrapper class for validation using vee-validate.
 */
export class ExtendedDialogValidator<FormType> {
    private readonly _form: FormType;

    /**
     * @param form - The vee-validate form to use.
     */
    public constructor(form: FormType) {
        this._form = form;
    }

    /**
     * The `defineComponentBinds` function.
     */
    public get defineComponentBinds() {
        // @ts-ignore
        return this._form.defineComponentBinds;
    }

    /** Validate the form. */
    public get validate() {
        // @ts-ignore
        return this._form.validate;
    }

    /**
     * The `handleSubmit` function.
     */
    public get handleSubmit() {
        // @ts-ignore
        return this._form.handleSubmit;
    }

    /**
     * A collection of all errors.
     */
    public get errors() {
        // @ts-ignore
        return this._form.errors;
    }
}

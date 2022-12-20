const orget2FormBox = document?.querySelector(".forget2-form-box");
const fields = document?.querySelectorAll(".forget-form__input");

fields[0]?.focus();

function handleInputField({ target }) {
  const value = target.value.slice(0, 1);
  target.value = value;

  const step = value ? 1 : -1;
  const fieldIndex = [...fields].findIndex((field) => field === target);
  const focusToIndex = fieldIndex + step;

  if (focusToIndex < 0 || focusToIndex >= fields.length) return;

  fields[focusToIndex].focus();
}
fields?.forEach((field) => {
  field?.addEventListener("input", handleInputField);
});





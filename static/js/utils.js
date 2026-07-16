export function getErrorMessage(error){
    if (typeof error.detail === "string") {
        return error.detail
    }else if (Array.isArray(error.detail)){
        return error.detail.map(err => err.msg).join(". ")
    }
    return "An error occured. Please try again."
}


export function showModal(modalId){
    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById(modalId)
    )
    modal.show()
    return modal
}

export function hideModal(modalId){
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) modal.hide();
}

export function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Truncate text at a word boundary, appending an ellipsis when shortened.
export function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  const sliced = text.slice(0, maxLength);
  const lastSpace = sliced.lastIndexOf(" ");
  const cut = lastSpace > 0 ? sliced.slice(0, lastSpace) : sliced;
  return cut.trimEnd() + "…";
}

export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "2-digit",
  });
}
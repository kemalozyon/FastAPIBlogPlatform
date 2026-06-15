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

export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "2-digit",
  });
}
async function unregisterParticipant(activity, email) {
  try {
    const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`, {
      method: "DELETE",
    });
    const result = await response.json();
    if (!response.ok) {
      console.error("Error unregistering participant:", result);
    }
  } catch (error) {
    console.error("Error unregistering participant:", error);
  }
}
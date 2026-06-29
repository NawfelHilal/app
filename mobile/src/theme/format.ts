export function formatEuro(cents: number): string {
  return `${(cents / 100).toFixed(2)} EUR`;
}

export function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    REQUESTED: 'Recherche chauffeur',
    ACCEPTED: 'Chauffeur en route',
    IN_PROGRESS: 'Course en cours',
    COMPLETED: 'Terminee',
    CANCELED: 'Annulee',
  };
  return labels[status] || status;
}


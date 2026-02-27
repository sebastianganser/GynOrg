import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobPositionService } from '../services/jobPositionService';
import { JobPosition, JobPositionCreate, JobPositionUpdate } from '../types/jobPosition';

export const JobPositionManager: React.FC = () => {
    const queryClient = useQueryClient();
    const [isAdding, setIsAdding] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [formData, setFormData] = useState<{ name: string; description: string; active: boolean }>({
        name: '',
        description: '',
        active: true
    });
    const [error, setError] = useState<string | null>(null);

    // Fetch positions
    const { data: positions, isLoading, isError } = useQuery<JobPosition[]>({
        queryKey: ['jobPositions'],
        queryFn: () => jobPositionService.getPositions(false)
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: (data: JobPositionCreate) => jobPositionService.createPosition(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['jobPositions'] });
            setIsAdding(false);
            resetForm();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Fehler beim Erstellen der Position');
        }
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number, data: JobPositionUpdate }) =>
            jobPositionService.updatePosition(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['jobPositions'] });
            setEditingId(null);
            resetForm();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Fehler beim Aktualisieren der Position');
        }
    });

    const resetForm = () => {
        setFormData({ name: '', description: '', active: true });
        setError(null);
    };

    const handleEdit = (position: JobPosition) => {
        setFormData({
            name: position.name,
            description: position.description || '',
            active: position.active
        });
        setEditingId(position.id);
        setIsAdding(false);
        setError(null);
    };

    const handleCancel = () => {
        setIsAdding(false);
        setEditingId(null);
        resetForm();
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!formData.name.trim()) {
            setError('Der Name der Position ist erforderlich.');
            return;
        }

        if (isAdding) {
            createMutation.mutate({
                name: formData.name.trim(),
                description: formData.description.trim() || undefined,
                active: formData.active
            });
        } else if (editingId !== null) {
            updateMutation.mutate({
                id: editingId,
                data: {
                    name: formData.name.trim(),
                    description: formData.description.trim() || undefined,
                    active: formData.active
                }
            });
        }
    };

    const toggleActive = (position: JobPosition) => {
        updateMutation.mutate({
            id: position.id,
            data: { active: !position.active }
        });
    };

    if (isLoading) return <div className="p-4 text-gray-500">Lade Positionen...</div>;
    if (isError) return <div className="p-4 text-red-500">Fehler beim Laden der Positionen.</div>;

    return (
        <div className="bg-white rounded-lg shadow mt-6">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-semibold text-gray-900">Mitarbeiter-Positionen</h2>
                    <p className="mt-1 text-sm text-gray-500">
                        Verwalten Sie hier die Liste der verfügbaren Job-Positionen für Mitarbeiter.
                    </p>
                </div>
                {!isAdding && editingId === null && (
                    <button
                        onClick={() => {
                            resetForm();
                            setIsAdding(true);
                        }}
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                        Neue Position
                    </button>
                )}
            </div>

            <div className="p-6">
                {error && (
                    <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                        {error}
                    </div>
                )}

                {(isAdding || editingId !== null) && (
                    <form onSubmit={handleSubmit} className="mb-6 bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <h3 className="text-lg font-medium mb-4">
                            {isAdding ? 'Neue Position hinzufügen' : 'Position bearbeiten'}
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Name der Position *
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    placeholder="z.B. Medizinische Fachangestellte"
                                    autoFocus
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Beschreibung (Optional)
                                </label>
                                <input
                                    type="text"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>
                        </div>

                        <div className="flex items-center mb-4">
                            <input
                                type="checkbox"
                                id="active"
                                checked={formData.active}
                                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                                Aktiv (kann Mitarbeitern zugewiesen werden)
                            </label>
                        </div>

                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={handleCancel}
                                className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="submit"
                                disabled={createMutation.isPending || updateMutation.isPending}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                Speichern
                            </button>
                        </div>
                    </form>
                )}

                {positions && positions.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Name
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Beschreibung
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Aktionen
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {positions.map((pos) => (
                                    <tr key={pos.id} className={!pos.active ? "bg-gray-50" : ""}>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className={`text-sm font-medium ${pos.active ? 'text-gray-900' : 'text-gray-500'}`}>
                                                {pos.name}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className={`text-sm ${pos.active ? 'text-gray-500' : 'text-gray-400'}`}>
                                                {pos.description || '-'}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${pos.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                                }`}>
                                                {pos.active ? 'Aktiv' : 'Inaktiv'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => handleEdit(pos)}
                                                disabled={isAdding || editingId !== null}
                                                className="text-blue-600 hover:text-blue-900 mr-4 disabled:opacity-50"
                                            >
                                                Bearbeiten
                                            </button>
                                            <button
                                                onClick={() => toggleActive(pos)}
                                                disabled={isAdding || editingId !== null || updateMutation.isPending}
                                                className={`${pos.active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'} disabled:opacity-50`}
                                            >
                                                {pos.active ? 'Deaktivieren' : 'Aktivieren'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                        Es wurden noch keine Positionen angelegt.
                    </div>
                )}
            </div>
        </div>
    );
};

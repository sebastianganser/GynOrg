import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { absenceTypeService } from '../services/absenceTypeService';
import { AbsenceType, AbsenceTypeCreate, AbsenceTypeUpdate, AbsenceTypeCategory } from '../types/absenceType';

const getCategoryLabel = (category: AbsenceTypeCategory) => {
    const labels: Record<AbsenceTypeCategory, string> = {
        [AbsenceTypeCategory.VACATION]: 'Urlaub',
        [AbsenceTypeCategory.SICK_LEAVE]: 'Krankheit',
        [AbsenceTypeCategory.TRAINING]: 'Fortbildung',
        [AbsenceTypeCategory.SPECIAL_LEAVE]: 'Sonderurlaub',
        [AbsenceTypeCategory.UNPAID_LEAVE]: 'Unbezahlter Urlaub',
        [AbsenceTypeCategory.OTHER]: 'Sonstiges',
    };
    return labels[category] || category;
};

export const AbsenceTypeManager: React.FC = () => {
    const queryClient = useQueryClient();
    const [isAdding, setIsAdding] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [formData, setFormData] = useState<{
        name: string;
        category: AbsenceTypeCategory;
        color: string;
        is_paid: boolean;
        requires_approval: boolean;
        description: string;
        active: boolean;
    }>({
        name: '',
        category: AbsenceTypeCategory.VACATION,
        color: '#3B82F6',
        is_paid: true,
        requires_approval: false,
        description: '',
        active: true
    });
    const [error, setError] = useState<string | null>(null);

    // Fetch absence types
    const { data: absenceTypes, isLoading, isError } = useQuery<AbsenceType[]>({
        queryKey: ['absenceTypes'],
        queryFn: () => absenceTypeService.getAbsenceTypes(false)
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: (data: AbsenceTypeCreate) => absenceTypeService.createAbsenceType(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['absenceTypes'] });
            setIsAdding(false);
            resetForm();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Fehler beim Erstellen des Abwesenheitstyps');
        }
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: number, data: AbsenceTypeUpdate }) =>
            absenceTypeService.updateAbsenceType(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['absenceTypes'] });
            setEditingId(null);
            resetForm();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Fehler beim Aktualisieren des Abwesenheitstyps');
        }
    });

    const resetForm = () => {
        setFormData({
            name: '',
            category: AbsenceTypeCategory.VACATION,
            color: '#3B82F6',
            is_paid: true,
            requires_approval: false,
            description: '',
            active: true
        });
        setError(null);
    };

    const handleEdit = (type: AbsenceType) => {
        setFormData({
            name: type.name,
            category: type.category,
            color: type.color || '#3B82F6',
            is_paid: type.is_paid,
            requires_approval: type.requires_approval,
            description: type.description || '',
            active: type.active
        });
        setEditingId(type.id);
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

        const typeName = getCategoryLabel(formData.category);

        const dataToSubmit = {
            name: typeName,
            category: formData.category,
            color: formData.color,
            is_paid: formData.is_paid,
            requires_approval: formData.requires_approval,
            description: formData.description.trim() || undefined,
            active: formData.active
        };

        if (isAdding) {
            createMutation.mutate(dataToSubmit);
        } else if (editingId !== null) {
            updateMutation.mutate({
                id: editingId,
                data: dataToSubmit
            });
        }
    };

    const toggleActive = (type: AbsenceType) => {
        updateMutation.mutate({
            id: type.id,
            data: { active: !type.active }
        });
    };

    const PREDEFINED_COLORS = [
        '#EF4444', // Red
        '#F97316', // Orange
        '#F59E0B', // Amber
        '#EAB308', // Yellow
        '#84CC16', // Lime
        '#22C55E', // Green
        '#10B981', // Emerald
        '#14B8A6', // Teal
        '#06B6D4', // Cyan
        '#0EA5E9', // Sky
        '#3B82F6', // Blue
        '#6366F1', // Indigo
        '#8B5CF6', // Violet
        '#D946EF', // Fuchsia
        '#EC4899', // Pink
        '#64748B', // Slate
    ];

    if (isLoading) return <div className="p-4 text-gray-500">Lade Abwesenheitstypen...</div>;
    if (isError) return <div className="p-4 text-red-500">Fehler beim Laden der Abwesenheitstypen.</div>;

    return (
        <div className="bg-white rounded-lg shadow mt-6">
            <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-semibold text-gray-900">Abwesenheitstypen</h2>
                    <p className="mt-1 text-sm text-gray-500">
                        Verwalten Sie hier die Liste der verfügbaren Kategorien für Abwesenheiten.
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
                        Neuer Typ
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
                            {isAdding ? 'Neuen Abwesenheitstyp hinzufügen' : 'Abwesenheitstyp bearbeiten'}
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Abwesenheitstyp *
                                </label>
                                <select
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value as AbsenceTypeCategory })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white"
                                    autoFocus
                                >
                                    {Object.values(AbsenceTypeCategory).map(cat => (
                                        <option key={cat} value={cat}>{getCategoryLabel(cat)}</option>
                                    ))}
                                </select>
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

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Farbe (Darstellung im Kalender) *
                            </label>
                            <div className="flex flex-wrap gap-2">
                                {PREDEFINED_COLORS.map(color => (
                                    <button
                                        key={color}
                                        type="button"
                                        className={`w-6 h-6 rounded-full focus:outline-none transition-transform ${formData.color === color ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''}`}
                                        style={{ backgroundColor: color }}
                                        onClick={() => setFormData(prev => ({ ...prev, color }))}
                                        title={color}
                                    />
                                ))}
                                <div className="flex items-center ml-2 border border-gray-300 rounded overflow-hidden">
                                    <input
                                        type="color"
                                        value={formData.color}
                                        onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
                                        className="w-8 h-8 cursor-pointer p-0 border-0"
                                        title="Eigene Farbe"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-wrap gap-4 mb-4 mt-4">
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_paid"
                                    checked={formData.is_paid}
                                    onChange={(e) => setFormData({ ...formData, is_paid: e.target.checked })}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="is_paid" className="ml-2 block text-sm text-gray-700">
                                    Wird bezahlt
                                </label>
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="requires_approval"
                                    checked={formData.requires_approval}
                                    onChange={(e) => setFormData({ ...formData, requires_approval: e.target.checked })}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="requires_approval" className="ml-2 block text-sm text-gray-700">
                                    Erfordert Genehmigung
                                </label>
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="active"
                                    checked={formData.active}
                                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                                    Aktiv (kann ausgewählt werden)
                                </label>
                            </div>
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

                {absenceTypes && absenceTypes.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Typ
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Eigenschaften
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
                                {absenceTypes.map((type) => (
                                    <tr key={type.id} className={!type.active ? "bg-gray-50" : ""}>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div
                                                    className="w-4 h-4 rounded-full mr-3 shrink-0"
                                                    style={{ backgroundColor: type.color || '#3B82F6' }}
                                                />
                                                <div className={`text-sm font-medium ${type.active ? 'text-gray-900' : 'text-gray-500'}`}>
                                                    {type.name}
                                                </div>
                                            </div>
                                            {type.description && (
                                                <div className="text-xs text-gray-500 mt-1 ml-7 truncate max-w-[200px]">
                                                    {type.description}
                                                </div>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex flex-col space-y-1">
                                                <span className={`px-2 py-0.5 inline-flex text-xs leading-4 rounded ${type.is_paid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                    {type.is_paid ? 'Bezahlt' : 'Unbezahlt'}
                                                </span>
                                                {type.requires_approval && (
                                                    <span className="px-2 py-0.5 inline-flex text-xs leading-4 rounded bg-yellow-100 text-yellow-800">
                                                        Mit Genehmigung
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${type.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                                {type.active ? 'Aktiv' : 'Inaktiv'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => handleEdit(type)}
                                                disabled={isAdding || editingId !== null}
                                                className="text-blue-600 hover:text-blue-900 mr-4 disabled:opacity-50"
                                            >
                                                Bearbeiten
                                            </button>
                                            <button
                                                onClick={() => toggleActive(type)}
                                                disabled={isAdding || editingId !== null || updateMutation.isPending}
                                                className={`${type.active ? 'text-orange-600 hover:text-orange-900' : 'text-green-600 hover:text-green-900'} disabled:opacity-50`}
                                            >
                                                {type.active ? 'Deaktivieren' : 'Aktivieren'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                        Es wurden noch keine Abwesenheitstypen angelegt.
                    </div>
                )}
            </div>
        </div>
    );
};

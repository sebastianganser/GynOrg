import React, { useState, useEffect } from 'react';
import { Employee } from '../types/employee';
import { VacationEntitlement } from '../types/vacationEntitlement';
import { VacationAllowance } from '../types/vacationAllowance';
import { vacationEntitlementService } from '../services/vacationEntitlementService';
import { vacationAllowanceService } from '../services/vacationAllowanceService';
import { Trash2, Plus, AlertCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from './ui/table';

interface VacationEntitlementManagerProps {
    employee: Employee;
}

type Tab = 'rules' | 'allowances';

export const VacationEntitlementManager: React.FC<VacationEntitlementManagerProps> = ({ employee }) => {
    const [activeTab, setActiveTab] = useState<Tab>('rules');

    // Entitlements State
    const [entitlements, setEntitlements] = useState<VacationEntitlement[]>([]);
    const [newDate, setNewDate] = useState('');
    const [newDays, setNewDays] = useState('30');

    // Allowances State
    const [allowances, setAllowances] = useState<VacationAllowance[]>([]);
    const [newAllowanceYear, setNewAllowanceYear] = useState(new Date().getFullYear().toString());
    const [newCarryover, setNewCarryover] = useState('0');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const loadData = async () => {
        setLoading(true);
        try {
            const [entitlementData, allowanceData] = await Promise.all([
                vacationEntitlementService.getEntitlements(employee.id),
                vacationAllowanceService.getAllowances(employee.id)
            ]);
            setEntitlements(entitlementData);
            setAllowances(allowanceData.sort((a, b) => b.year - a.year));
        } catch (e: any) {
            console.error(e);
            setError('Fehler beim Laden der Daten.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (employee?.id) {
            loadData();
        }
    }, [employee]);

    const handleAddEntitlement = async () => {
        if (!newDate || !newDays) return;
        setLoading(true);
        setError('');
        try {
            await vacationEntitlementService.createEntitlement({
                employee_id: employee.id,
                from_date: newDate,
                days: parseInt(newDays)
            });
            setNewDate('');
            await loadData();
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteEntitlement = async (id: number) => {
        if (!window.confirm('Möchten Sie diesen Eintrag wirklich löschen?')) return;
        try {
            await vacationEntitlementService.deleteEntitlement(id);
            await loadData();
        } catch (e: any) {
            setError(e.message);
        }
    };

    const handleAddAllowance = async () => {
        if (!newAllowanceYear) return;
        setLoading(true);
        setError('');
        try {
            // Check if year already exists
            const existing = allowances.find(a => a.year === parseInt(newAllowanceYear));
            if (existing) {
                // Update existing
                await vacationAllowanceService.updateAllowance(existing.id, {
                    carryover_days: parseInt(newCarryover)
                });
            } else {
                // Find effective annual allowance for this year
                const yearDate = new Date(`${newAllowanceYear}-01-01`);
                // Sort entitlements by date desc to find the active one
                const sortedEntitlements = [...entitlements].sort((a, b) =>
                    new Date(b.from_date).getTime() - new Date(a.from_date).getTime()
                );

                const activeRule = sortedEntitlements.find(e => new Date(e.from_date) <= yearDate);
                const annualDays = activeRule ? activeRule.days : 30; // Default fallback

                await vacationAllowanceService.createAllowance({
                    employee_id: employee.id,
                    year: parseInt(newAllowanceYear),
                    annual_allowance: annualDays,
                    carryover_days: parseInt(newCarryover)
                });
            }

            setNewAllowanceYear((parseInt(newAllowanceYear) + 1).toString());
            setNewCarryover('0');
            await loadData();
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex border-b border-gray-200">
                <button
                    className={`px-4 py-2 font-medium text-sm focus:outline-none ${activeTab === 'rules' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    onClick={() => setActiveTab('rules')}
                >
                    Allgemeine Regeln
                </button>
                <button
                    className={`px-4 py-2 font-medium text-sm focus:outline-none ${activeTab === 'allowances' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    onClick={() => setActiveTab('allowances')}
                >
                    Jahreskonten & Urlaubsstand
                </button>
            </div>

            {error && (
                <div className="bg-red-50 p-3 rounded-md text-red-600 text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    {error}
                </div>
            )}

            {activeTab === 'rules' && (
                <div className="space-y-6">
                    <div className="bg-blue-50 p-4 rounded-md text-sm text-blue-700">
                        Hier legen Sie fest, wie viel Urlaub dem Mitarbeiter <strong>pro Jahr</strong> grundsätzlich zusteht.
                        Änderungen gelten ab dem eingetragenen Datum für alle folgenden Jahre.
                    </div>

                    <div className="flex gap-4 items-end bg-gray-50 p-4 rounded-md border border-gray-100">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Ab Datum</label>
                            <Input
                                type="date"
                                value={newDate}
                                onChange={e => setNewDate(e.target.value)}
                                className="bg-white"
                            />
                        </div>
                        <div className="w-32">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Tage/Jahr</label>
                            <Input
                                type="number"
                                value={newDays}
                                onChange={e => setNewDays(e.target.value)}
                                min="0"
                                max="365"
                                className="bg-white"
                            />
                        </div>
                        <Button onClick={handleAddEntitlement} disabled={loading || !newDate} className="mb-[2px]">
                            <Plus className="w-4 h-4 mr-2" /> Regel hinzufügen
                        </Button>
                    </div>

                    <div className="border rounded-md overflow-hidden">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Gültig ab</TableHead>
                                    <TableHead>Anspruch (Tage)</TableHead>
                                    <TableHead className="text-right">Aktion</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {entitlements.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={3} className="text-center text-gray-500 py-8">
                                            Keine Regeln definiert.
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    entitlements.map(e => (
                                        <TableRow key={e.id}>
                                            <TableCell>{new Date(e.from_date).toLocaleDateString('de-DE')}</TableCell>
                                            <TableCell className="font-medium">{e.days}</TableCell>
                                            <TableCell className="text-right">
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handleDeleteEntitlement(e.id)}
                                                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            )}

            {activeTab === 'allowances' && (
                <div className="space-y-6">
                    <div className="bg-amber-50 p-4 rounded-md text-sm text-amber-800">
                        <strong>Resturlaub aus Vorjahren:</strong> Hier können Sie manuell eintragen, wenn ein Mitarbeiter Resturlaub aus einem Vorjahr mitbringt (z.B. bei Neueinstellung aus "undokumentierter Zeit").
                        Der Jahresanspruch wird automatisch aus den Regeln übernommen.
                    </div>

                    <div className="flex gap-4 items-end bg-gray-50 p-4 rounded-md border border-gray-100">
                        <div className="w-32">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Jahr</label>
                            <Input
                                type="number"
                                value={newAllowanceYear}
                                onChange={e => setNewAllowanceYear(e.target.value)}
                                min="2000"
                                max="2100"
                                className="bg-white"
                            />
                        </div>
                        <div className="w-48">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Resturlaub (Tage)</label>
                            <Input
                                type="number"
                                value={newCarryover}
                                onChange={e => setNewCarryover(e.target.value)}
                                min="0"
                                max="100"
                                className="bg-white"
                            />
                        </div>
                        <Button onClick={handleAddAllowance} disabled={loading} className="mb-[2px]">
                            <Plus className="w-4 h-4 mr-2" /> Speichern
                        </Button>
                    </div>

                    <div className="border rounded-md overflow-hidden">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Jahr</TableHead>
                                    <TableHead>Jahresanspruch</TableHead>
                                    <TableHead>Resturlaub (Vorjahr)</TableHead>
                                    <TableHead className="font-bold">Gesamt</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {allowances.length === 0 ? (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center text-gray-500 py-8">
                                            Keine Jahreskonten vorhanden.
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    allowances.map(a => (
                                        <TableRow key={a.id}>
                                            <TableCell className="font-medium">{a.year}</TableCell>
                                            <TableCell>{a.annual_allowance}</TableCell>
                                            <TableCell className="text-amber-600 font-medium">
                                                {a.carryover_days > 0 ? `+ ${a.carryover_days}` : '-'}
                                            </TableCell>
                                            <TableCell className="font-bold">{a.total_allowance}</TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            )}
        </div>
    );
};

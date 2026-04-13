import { useState, useEffect } from 'react';
import { Check, X, Edit3, Save, Plus, Trash2, Sparkles, Pill, UtensilsCrossed, Heart, Calendar } from 'lucide-react';
import { chatAPI } from '../services/api';

export default function RecommendationsPanel({ userMessage, onClose }) {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [editMode, setEditMode] = useState({
    medications: false,
    mealPlan: false,
    selfCare: false
  });

  useEffect(() => {
    generateRecommendations();
  }, []);

  const generateRecommendations = async () => {
    try {
      setLoading(true);
      const response = await chatAPI.generateRecommendations(userMessage);
      setRecommendations(response.recommendations);
    } catch (error) {
      console.error('Error generating recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    try {
      setApplying(true);
      const response = await chatAPI.applyRecommendations(recommendations._id || recommendations.recommendation_id);
      alert(`✅ Recommendations applied!\n${response.medications_added} medications and meal plan saved.`);
      onClose();
    } catch (error) {
      console.error('Error applying recommendations:', error);
      alert('Failed to apply recommendations. Please try again.');
    } finally {
      setApplying(false);
    }
  };

  const toggleEditMode = (section) => {
    setEditMode(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const updateMedication = (index, field, value) => {
    const updated = { ...recommendations };
    updated.recommendations.medications[index][field] = value;
    setRecommendations(updated);
  };

  const removeMedication = (index) => {
    const updated = { ...recommendations };
    updated.recommendations.medications.splice(index, 1);
    setRecommendations(updated);
  };

  const updateMealItem = (mealType, itemIndex, field, value) => {
    const updated = { ...recommendations };
    updated.recommendations.meal_plan[mealType][itemIndex][field] = value;
    setRecommendations(updated);
  };

  const removeMealItem = (mealType, itemIndex) => {
    const updated = { ...recommendations };
    updated.recommendations.meal_plan[mealType].splice(itemIndex, 1);
    setRecommendations(updated);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-card-dark rounded-xl p-8 max-w-md">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-900 dark:text-white font-semibold">Generating personalized recommendations...</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Analyzing your health needs</p>
          </div>
        </div>
      </div>
    );
  }

  if (!recommendations || !recommendations.recommendations) {
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-card-dark rounded-xl p-6 max-w-md">
          <p className="text-gray-900 dark:text-white">Unable to generate recommendations. Please try again.</p>
          <button onClick={onClose} className="mt-4 px-4 py-2 bg-primary text-white rounded-lg">Close</button>
        </div>
      </div>
    );
  }

  const recs = recommendations.recommendations;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white dark:bg-card-dark rounded-xl max-w-4xl w-full my-8 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-white" />
            <div>
              <h2 className="text-white text-xl font-bold">Personalized Health Recommendations</h2>
              <p className="text-blue-100 text-sm">AI-generated plan based on your needs</p>
            </div>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Medications Section */}
          {recs.medications && recs.medications.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Pill className="w-5 h-5 text-blue-600" />
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">Recommended Medications</h3>
                </div>
                <button
                  onClick={() => toggleEditMode('medications')}
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50"
                >
                  {editMode.medications ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
                  {editMode.medications ? 'Done' : 'Edit'}
                </button>
              </div>
              <div className="space-y-3">
                {recs.medications.map((med, index) => (
                  <div key={index} className="bg-white dark:bg-gray-900 rounded-lg p-4 flex items-start justify-between gap-4">
                    <div className="flex-1">
                      {editMode.medications ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={med.name}
                            onChange={(e) => updateMedication(index, 'name', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white"
                          />
                          <input
                            type="text"
                            value={med.dosage}
                            onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                            className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-gray-900 dark:text-white text-sm"
                          />
                        </div>
                      ) : (
                        <>
                          <p className="font-semibold text-gray-900 dark:text-white">{med.name}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{med.dosage} • {med.frequency}</p>
                          {med.notes && <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{med.notes}</p>}
                        </>
                      )}
                    </div>
                    {editMode.medications && (
                      <button
                        onClick={() => removeMedication(index)}
                        className="text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 p-2 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Meal Plan Section */}
          {recs.meal_plan && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <UtensilsCrossed className="w-5 h-5 text-green-600" />
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white">Daily Meal Plan</h3>
                </div>
                <button
                  onClick={() => toggleEditMode('mealPlan')}
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg hover:bg-green-200 dark:hover:bg-green-900/50"
                >
                  {editMode.mealPlan ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
                  {editMode.mealPlan ? 'Done' : 'Edit'}
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(recs.meal_plan).map(([mealType, items]) => (
                  <div key={mealType} className="bg-white dark:bg-gray-900 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white capitalize mb-3">{mealType}</h4>
                    <div className="space-y-2">
                      {items.map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-2 text-sm">
                          {editMode.mealPlan ? (
                            <>
                              <input
                                type="text"
                                value={item.name}
                                onChange={(e) => updateMealItem(mealType, idx, 'name', e.target.value)}
                                className="flex-1 px-2 py-1 bg-gray-50 dark:bg-gray-800 rounded text-gray-900 dark:text-white"
                              />
                              <button
                                onClick={() => removeMealItem(mealType, idx)}
                                className="text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 p-1 rounded"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </>
                          ) : (
                            <>
                              <span className="text-gray-700 dark:text-gray-300">{item.name}</span>
                              <span className="text-gray-500 dark:text-gray-400">{item.calories} cal</span>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Self-Care Tasks */}
          {recs.self_care && recs.self_care.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <Heart className="w-5 h-5 text-red-500" />
                <h3 className="font-bold text-lg text-gray-900 dark:text-white">Self-Care Activities</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recs.self_care.map((task, index) => (
                  <div key={index} className="bg-white dark:bg-gray-900 rounded-lg p-3 flex items-start gap-3">
                    <Check className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">{task.task}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{task.duration}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Foods to Include/Avoid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recs.foods_to_include && recs.foods_to_include.length > 0 && (
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h4 className="font-semibold text-green-800 dark:text-green-400 mb-2">✅ Foods to Include</h4>
                <ul className="space-y-1">
                  {recs.foods_to_include.map((food, idx) => (
                    <li key={idx} className="text-sm text-gray-700 dark:text-gray-300">• {food}</li>
                  ))}
                </ul>
              </div>
            )}
            {recs.foods_to_avoid && recs.foods_to_avoid.length > 0 && (
              <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
                <h4 className="font-semibold text-red-800 dark:text-red-400 mb-2">❌ Foods to Avoid</h4>
                <ul className="space-y-1">
                  {recs.foods_to_avoid.map((food, idx) => (
                    <li key={idx} className="text-sm text-gray-700 dark:text-gray-300">• {food}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* When to See Doctor */}
          {recs.when_to_see_doctor && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-lg p-4">
              <p className="text-sm text-gray-800 dark:text-gray-200">
                <strong>⚠️ When to see a doctor:</strong> {recs.when_to_see_doctor}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleApply}
              disabled={applying}
              className="flex-1 bg-primary hover:bg-blue-700 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {applying ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Applying...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  Apply All Recommendations
                </>
              )}
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

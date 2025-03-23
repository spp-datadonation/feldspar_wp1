// packages/data-collector/src/App.tsx
import { DataSubmissionPageFactory, ScriptHostComponent } from "@eyra/feldspar";
import React from "react";

function App() {
  return (
    <div className="App">
      <ScriptHostComponent
        workerUrl="./py_worker.js"
        standalone={process.env.NODE_ENV !== "production"}
        factories={[
          new DataSubmissionPageFactory({
            promptFactories: [
              // Add consent form factory 
              {
                create: (body: any, context: any) => {
                  if (body && body.__type__ === "PropsUIPromptConsentForm") {
                    // Custom consent form implementation
                    return (
                      <div className="consent-form p-4">
                        {body.description && (
                          <p className="text-bodylarge font-body mb-6">
                            {context.locale && body.description.translations
                              ? body.description.translations[context.locale] || 
                                Object.values(body.description.translations)[0]
                              : "Please review the data below"}
                          </p>
                        )}
                        
                        {/* Display tables */}
                        {body.tables && body.tables.map((table: any, index: number) => (
                          <div key={index} className="mb-6 border p-4 rounded">
                            <h3 className="font-bold mb-2">
                              {context.locale && table.title.translations
                                ? table.title.translations[context.locale] || 
                                  Object.values(table.title.translations)[0]
                                : "Data Table"}
                            </h3>
                            <p className="mb-4">
                              {context.locale && table.description.translations
                                ? table.description.translations[context.locale] || 
                                  Object.values(table.description.translations)[0]
                                : ""}
                            </p>
                            {/* Simple table view */}
                            <pre className="bg-gray-100 p-2 overflow-auto max-h-64">
                              {JSON.stringify(JSON.parse(table.data_frame), null, 2)}
                            </pre>
                          </div>
                        ))}
                        
                        {/* Donation buttons */}
                        <div className="mt-8">
                          <p className="mb-4">
                            {context.locale && body.donateQuestion && body.donateQuestion.translations
                              ? body.donateQuestion.translations[context.locale] || 
                                Object.values(body.donateQuestion.translations)[0]
                              : "Do you want to donate the above data?"}
                          </p>
                          
                          <div className="flex gap-4">
                            <button
                              onClick={() => context.resolve?.({ 
                                __type__: "PayloadJSON", 
                                value: JSON.stringify({}) 
                              })}
                              className="bg-success text-white px-4 py-2 rounded"
                            >
                              {context.locale && body.donateButton && body.donateButton.translations
                                ? body.donateButton.translations[context.locale] || 
                                  Object.values(body.donateButton.translations)[0]
                                : "Yes, donate"}
                            </button>
                            
                            <button
                              onClick={() => context.resolve?.({ 
                                __type__: "PayloadFalse", 
                                value: false 
                              })}
                              className="text-grey1 px-4 py-2"
                            >
                              No
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  }
                  
                  return null;
                }
              }
            ]
          })
        ]}
      />
    </div>
  );
}

export default App;

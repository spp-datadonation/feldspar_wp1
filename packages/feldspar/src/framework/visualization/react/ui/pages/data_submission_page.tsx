import React, { JSX, useCallback } from "react";
import { Weak } from "../../../../helpers";
import TextBundle from "../../../../text_bundle";
import { Translator } from "../../../../translator";
import { Translatable } from "../../../../types/elements";
import { PropsUIPageDataSubmission } from "../../../../types/pages";
import { ReactFactoryContext } from "../../factory";
import { Title1 } from "../elements/text";
import { Page } from "./templates/page";
import { createPromptFactoriesWithDefaults, PromptContext } from "../prompts/factory";

type Props = Weak<PropsUIPageDataSubmission> & ReactFactoryContext;

export const DataSubmissionPage = (props: Props): JSX.Element => {
  const { title } = prepareCopy(props);
  const { locale } = props;
  const promptFactories = createPromptFactoriesWithDefaults(
    props.promptFactories
  );
  const DataSubmissionData = React.useRef<Map<string, string>>(new Map());

  const onDataSubmissionDataChanged = useCallback((key: string, value: any)=> {
    console.log("onDataSubmissionDataChanged", key, value);
    DataSubmissionData.current.set(key, value);
  }, [DataSubmissionData]);

  function onDonate(): void {
    const DataSubmissionDataObject = Object.fromEntries(DataSubmissionData.current);
    console.log("onDonate", JSON.stringify(DataSubmissionDataObject));
    props.resolve?.({ __type__: "PayloadJSON", value: JSON.stringify(DataSubmissionDataObject) });
  }

  function renderBodyItem(bodyItem: any, context: PromptContext): JSX.Element | null {
    console.log("Body item to render:", bodyItem);
    console.log("Body item __type__:", bodyItem.__type__);
    console.log("Context:", context);

    for (const factory of promptFactories) {
      const element = factory.create(bodyItem, context);
      console.log("Trying factory:", factory.constructor.name);
      if (element !== null) {
        console.log("Found matching factory:", factory.constructor.name);
        return element;
      }
    }
    console.log("No factory found for body item");
    return null;
  }

  function renderBody(props: Props): JSX.Element[] {
    const context = { locale: locale, resolve: props.resolve, onDataSubmissionDataChanged, onDonate};
    const bodyItems = Array.isArray(props.body) ? props.body : [props.body];

    console.log("Number of body items:", bodyItems.length);

    return bodyItems.map((item, index) => {
      console.log(`Processing body item at index ${index}:`, item);
      const element = renderBodyItem(item, context);
      if (element === null) {
        console.error(`No factory found for body item at index ${index}:`, item);
        throw new TypeError(`No factory found for body item at index ${index}`);
      }
      return <React.Fragment key={index}>{element}</React.Fragment>;
    });
  }

  const body: JSX.Element = (
    <>
      <Title1 text={title} />
      {renderBody(props)}
    </>
  );

  return <Page body={body} />;
};

interface Copy {
  title: string;
}

function prepareCopy({ header: { title }, locale }: Props): Copy {
  return {
    title: Translator.translate(title, locale),
  };
}

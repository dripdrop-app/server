import React, { useContext, useMemo } from 'react';

interface ConsumerComponentProps<T, K> {
	context: React.Context<T>;
	selector: (contextValue: T) => K;
	render: (props: K) => JSX.Element;
}

export const ConsumerComponent = <T, K>(props: ConsumerComponentProps<T, K>) => {
	const contextValue = useContext(props.context);
	const selectedValues = props.selector(contextValue);
	const { render } = props;

	return useMemo(() => render(selectedValues), [render, selectedValues]);
};

import { useCallback, useEffect, useState, ComponentType, ComponentPropsWithRef, useMemo, Fragment } from 'react';

interface InfiniteScrollProps<T> {
	items: T[];
	loading: boolean;
	components: {
		Parent: ComponentType<ComponentPropsWithRef<'div'>>;
		Loader: ComponentType<ComponentPropsWithRef<'div'>>;
	};
	renderItem: (item: T, index: number) => JSX.Element | JSX.Element[];
	onEndReached: () => void;
}

const InfiniteScroll = <T,>(props: InfiniteScrollProps<T>) => {
	const { items, renderItem, onEndReached, components, loading } = props;
	const { Parent, Loader } = components;

	const [showScrollButton, setShowScrollButton] = useState(false);

	const onGridBottom = useCallback(() => {
		if (document.body.offsetHeight - 1000 < window.innerHeight + window.scrollY) {
			if (!loading) {
				onEndReached();
			}
		}
	}, [loading, onEndReached]);

	const updateScrollButton = useCallback(() => {
		if (window.scrollY > 0 && !showScrollButton) {
			setShowScrollButton(true);
		} else if (window.scrollY === 0 && showScrollButton) {
			setShowScrollButton(false);
		}
	}, [showScrollButton]);

	const RenderItems = useMemo(
		() => items.map((item, index) => <Fragment key={`scroll-item-${index}`}>{renderItem(item, index)}</Fragment>),
		[items, renderItem]
	);

	useEffect(() => {
		window.addEventListener('scroll', updateScrollButton);
		window.addEventListener('scroll', onGridBottom);
		return () => {
			window.removeEventListener('scroll', onGridBottom);
			window.removeEventListener('scroll', updateScrollButton);
		};
	}, [loading, onGridBottom, updateScrollButton]);

	return useMemo(
		() => (
			<Fragment>
				<Parent>{RenderItems}</Parent>
				{loading ? <Loader /> : null}
			</Fragment>
		),
		[Loader, Parent, RenderItems, loading]
	);
};

export default InfiniteScroll;

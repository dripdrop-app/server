import { useCallback, useEffect, useState, useMemo, Fragment } from 'react';
import { Box, Fab } from '@mui/material';
import { ArrowUpward } from '@mui/icons-material';

interface InfiniteScrollProps<T> {
	items: T[];
	threshold?: number;
	renderItem: (item: T, index: number) => JSX.Element | JSX.Element[];
	onEndReached: () => void;
}

const InfiniteScroll = <T,>(props: InfiniteScrollProps<T>) => {
	const { items, renderItem, onEndReached, threshold } = props;

	const [showScrollButton, setShowScrollButton] = useState(false);

	const onGridBottom = useCallback(() => {
		if (document.body.offsetHeight - (threshold ?? 1000) < window.innerHeight + window.scrollY) {
			onEndReached();
		}
	}, [onEndReached, threshold]);

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
	}, [onGridBottom, updateScrollButton]);

	return useMemo(
		() => (
			<Box>
				<Fab
					sx={{
						position: 'fixed',
						bottom: '5vh',
						right: '5vw',
						display: showScrollButton ? 'block' : 'none',
						zIndex: (theme) => theme.zIndex.fab,
					}}
					color="primary"
					onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
				>
					<ArrowUpward />
				</Fab>
				<Box>{RenderItems}</Box>
			</Box>
		),
		[RenderItems, showScrollButton]
	);
};

export default InfiniteScroll;

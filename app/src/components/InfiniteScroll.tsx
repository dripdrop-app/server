import React, { useCallback, useEffect, useState, useRef } from 'react';
import { Box, Fab } from '@mui/material';
import { ArrowUpward } from '@mui/icons-material';
import ConditionalDisplay from './ConditionalDisplay';

interface InfiniteScrollProps<T> {
	items: T[];
	renderItem: (item: T, index: number) => JSX.Element | JSX.Element[];
	onEndReached?: () => void;
	parentRef?: React.RefObject<HTMLElement>;
}

const InfiniteScroll = <T,>(props: InfiniteScrollProps<T>) => {
	const { items, renderItem, onEndReached, parentRef } = props;
	const [showScrollButton, setShowScrollButton] = useState(false);

	const boxRef = useRef<HTMLDivElement>();

	const onGridBottom = useCallback(() => {
		if (parentRef && parentRef.current) {
			const parent = parentRef.current;
			if (parent.offsetHeight + parent.scrollTop > parent.scrollHeight - 500 && onEndReached) {
				onEndReached();
			}
		} else {
			if (document.body.offsetHeight - 500 < window.innerHeight + window.scrollY && onEndReached) {
				onEndReached();
			}
		}
	}, [onEndReached, parentRef]);

	const updateScrollButton = useCallback(() => {
		if (boxRef.current) {
			const grid = boxRef.current;
			const gridCoordinates = grid.getBoundingClientRect();
			if (gridCoordinates.y < 0 && !showScrollButton) {
				setShowScrollButton(true);
			} else if (gridCoordinates.y > 0 && showScrollButton) {
				setShowScrollButton(false);
			}
		}
	}, [showScrollButton]);

	useEffect(() => {
		const parent = parentRef && parentRef.current ? parentRef.current : window;
		if (parent) {
			parent.addEventListener('scroll', updateScrollButton);
			parent.addEventListener('scroll', onGridBottom);
			return () => {
				parent.removeEventListener('scroll', onGridBottom);
				parent.removeEventListener('scroll', updateScrollButton);
			};
		}
	}, [onGridBottom, parentRef, updateScrollButton]);

	return (
		<Box>
			<Box ref={boxRef}>
				{items.map((item, index) => (
					<React.Fragment key={`scroll-item-${index}`}>{renderItem(item, index)}</React.Fragment>
				))}
			</Box>
			<ConditionalDisplay condition={showScrollButton}>
				<Box
					sx={{
						position: 'fixed',
						right: '5vw',
						bottom: '10vh',
					}}
				>
					<Fab
						variant="circular"
						color="primary"
						onClick={() => {
							if (boxRef.current) {
								const parent = parentRef && parentRef.current ? parentRef.current : window;
								parent.scrollTo({ top: 0, behavior: 'smooth' });
							}
						}}
					>
						<ArrowUpward />
					</Fab>
				</Box>
			</ConditionalDisplay>
		</Box>
	);
};

export default InfiniteScroll;

import React, { useState, useMemo, useEffect } from 'react';
import { isEqual } from 'lodash';
import { useYoutubeVideosQuery } from '../../../api/youtube';
import { CircularProgress } from '@mui/material';

interface YoutubeVideosPageProps extends YoutubeVideosBody {
	renderItem: (video: YoutubeVideo, index: number) => JSX.Element;
	onLoading?: (page: number) => void;
	onLoaded?: (page: number, videos: YoutubeVideo[]) => void;
}

const YoutubeVideosPage = (props: YoutubeVideosPageProps) => {
	const { renderItem, onLoaded, onLoading } = props;
	const [args, setArgs] = useState<YoutubeVideosBody>({
		perPage: props.perPage,
		page: props.page,
		channelID: props.channelID,
		selectedCategories: props.selectedCategories,
		queuedOnly: props.queuedOnly,
		likedOnly: props.likedOnly,
	});

	const videosStatus = useYoutubeVideosQuery(args);

	const videos = useMemo(
		() => (videosStatus.isSuccess && videosStatus.currentData ? videosStatus.currentData.videos : []),
		[videosStatus.currentData, videosStatus.isSuccess]
	);

	const itemsToRender = useMemo(() => {
		if (videosStatus.isLoading) {
			return <CircularProgress />;
		}

		return videos.map((video, i) => (
			<React.Fragment key={`item-${args.page}-${i}`}>{renderItem(video, i)}</React.Fragment>
		));
	}, [videosStatus.isLoading, videos, args.page, renderItem]);

	useEffect(() => {
		if (onLoaded && videosStatus.isSuccess && videosStatus.currentData) {
			onLoaded(args.page, videosStatus.currentData.videos);
		}
	}, [args.page, onLoaded, videosStatus.currentData, videosStatus.isSuccess]);

	useEffect(() => {
		if (onLoading && (videosStatus.isLoading || videosStatus.isFetching)) {
			onLoading(args.page);
		}
	}, [args.page, onLoading, videosStatus.isFetching, videosStatus.isLoading]);

	useEffect(() => {
		const selectedProps = {
			perPage: props.perPage,
			page: props.page,
			channelID: props.channelID,
			selectedCategories: props.selectedCategories,
			queuedOnly: props.queuedOnly,
			likedOnly: props.likedOnly,
		};
		if (!isEqual(selectedProps, args)) {
			setArgs(selectedProps);
		}
	}, [args, props]);

	return <React.Fragment>{itemsToRender}</React.Fragment>;
};

export default YoutubeVideosPage;

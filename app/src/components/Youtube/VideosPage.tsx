import { Fragment, useMemo } from 'react';
import { useYoutubeVideosQuery } from '../../api/youtube';

interface VideosPageProps extends YoutubeVideosBody {
	renderItem: (video: YoutubeVideo, index: number) => JSX.Element;
	renderLoading: () => JSX.Element;
}

const VideosPage = (props: VideosPageProps) => {
	const { renderItem, renderLoading } = props;

	const videosStatus = useYoutubeVideosQuery(props);

	const videos = useMemo(
		() => (videosStatus.isSuccess && videosStatus.currentData ? videosStatus.currentData.videos : []),
		[videosStatus.currentData, videosStatus.isSuccess]
	);

	const LoadingItem = useMemo(() => renderLoading(), [renderLoading]);

	return useMemo(
		() => (
			<Fragment>
				<div style={{ display: videosStatus.isLoading ? 'contents' : 'none' }}>{LoadingItem}</div>
				{videos.map((video, i) => (
					<Fragment key={video.id}>{renderItem(video, i)}</Fragment>
				))}
			</Fragment>
		),
		[LoadingItem, renderItem, videos, videosStatus.isLoading]
	);
};

export default VideosPage;

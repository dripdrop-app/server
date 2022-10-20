import { Fragment, useMemo } from 'react';
import { useYoutubeVideosQuery } from '../../../api/youtube';

interface YoutubeVideosPageProps extends YoutubeVideosBody {
	renderItem: (video: YoutubeVideo, index: number) => JSX.Element;
}

const YoutubeVideosPage = (props: YoutubeVideosPageProps) => {
	const { renderItem } = props;

	const videosStatus = useYoutubeVideosQuery(props);

	const videos = useMemo(
		() => (videosStatus.isSuccess && videosStatus.currentData ? videosStatus.currentData.videos : []),
		[videosStatus.currentData, videosStatus.isSuccess]
	);

	return (
		<Fragment>
			{videos.map((video, i) => (
				<Fragment key={video.id}>{renderItem(video, i)}</Fragment>
			))}
		</Fragment>
	);
};

export default YoutubeVideosPage;
